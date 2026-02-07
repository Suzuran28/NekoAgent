from langchain.agents.middleware import before_model, wrap_tool_call, SummarizationMiddleware
from langchain.tools.tool_node import ToolCallRequest
from typing import Callable
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from utils.logger import get_logger
from utils.config_ import config
from models.factory import OllamaChatModel
from utils.prompt_loader import load_prompt
from langchain.agents.middleware.summarization import DEFAULT_SUMMARY_PROMPT

logger = get_logger("Middleware")

@wrap_tool_call
def monitor_tool_call(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command]
) -> ToolMessage | Command:
    if config["Debug"]:
        logger.debug(f"[Tool] 执行工具: {request.tool_call["name"]}")
        logger.debug(f"[Tool] 工具参数: {request.tool_call['args']}")
        
    try:
        result = handler(request)
        logger.info(f"[Tool] 工具 {request.tool_call['name']} 执行成功")
        return result
    except Exception as e:
        logger.error(f"[Tool] 工具 {request.tool_call['name']} 执行失败, 原因: {str(e)}")
        raise e
    
@before_model
def monitor_model(
    state: AgentState,
    runtime: Runtime
) -> None:
    logger.info(f"[Model] 开始执行模型 {config['models']['chat_model']}, 带有 {len(state['messages'])} 条消息")
    
    if config["Debug"]:
        logger.debug(f"[Model] {type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}") # pyright: ignore[reportAttributeAccessIssue]

def get_summarization_middleware():
    types = config["history"]["trigger"]["type"]
    values = config["history"]["trigger"]["value"]

    if config["Debug"]:
        logger.debug(f"[Middleware] types_type: {type(types)} value_type: {type(types[0])}")
        logger.debug(f"[Middleware] values_type: {type(values)} value_type: {type(values[0])}")
    
    if type(types) != list or type(values) != list:
        logger.error("配置文件错误: history.trigger.type 和 history.trigger.value 必须是列表")
        raise Exception("配置文件错误: history.trigger.type 和 history.trigger.value 必须是列表")
        
    if len(types) != len(values):
        logger.error("配置文件错误: history.trigger.type 和 history.trigger.value 的长度必须一致")
        raise Exception("配置文件错误: history.trigger.type 和 history.trigger.value 的长度必须一致")
        
    trigger = list(zip(types, values))

    model = OllamaChatModel().generator(config["models"]["history_summary"])
    
    summary_prompt = load_prompt(config["prompts"]["history_summary_prompt"])
    if not summary_prompt:
        summary_prompt = DEFAULT_SUMMARY_PROMPT
        logger.warning("[Middleware] 未找到历史摘要提示词, 使用默认提示词")
        
    if config["Debug"]:
        logger.debug(f"[Middleware]模型 {model}")
        logger.debug(f"[Middleware]触发器 {type(trigger)} {trigger} value_type: {type(trigger[0])} inner_type: {type(trigger[0][0])} {type(trigger[0][1])}")
    
    try:
        middleware = SummarizationMiddleware(model= model, trigger= trigger, prompt= summary_prompt)
        logger.info(f"[Middleware] 加载历史摘要中间件成功")
        return middleware
    except Exception as e:
        logger.warning(f"[Middleware] 加载历史摘要中间件失败, 错误: {str(e)}")
        raise e