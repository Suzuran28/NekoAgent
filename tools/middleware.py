from langchain.agents.middleware import before_agent, before_model, after_agent, after_model, wrap_model_call, wrap_tool_call, dynamic_prompt
from langchain.tools.tool_node import ToolCallRequest
from typing import Callable
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from utils.logger import get_logger
from utils.config_ import config

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