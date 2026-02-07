from langchain.agents import create_agent
from models.factory import OllamaChatModel
from utils.config_ import config
from utils.prompt_loader import load_prompt
from utils.logger import get_logger
from tools.tools import get_rag, get_weather, get_time, get_weather_by_city, get_emoji, check_file, check_filelist, modify_file
from tools.middleware import monitor_tool_call, monitor_model, get_summarization_middleware
from langgraph.checkpoint.memory import InMemorySaver

logger = get_logger("Agent")

class ReactAgent:
    def __init__(self, checkpoint):
        super().__init__()
        self.agent = create_agent(
            model= OllamaChatModel().generator(config["models"]["chat_model"]),
            tools= [get_rag, get_time, get_weather, get_weather_by_city, get_emoji, check_file, check_filelist, modify_file],
            middleware= [monitor_tool_call, monitor_model, get_summarization_middleware()],
            checkpointer= checkpoint,
            system_prompt= load_prompt(config["prompts"]["system_prompt"]),
        )
        
    def excute_stream(self, inputs: str, session_config: dict):
        stream = self.agent.stream(
            {
                "messages": [
                    {"role": "user", "content": inputs}
                ]
            },
            session_config, # pyright: ignore[reportArgumentType]
            stream_mode= "values"
        )
        
        for chunk in stream:
            latest_message = chunk["messages"][-1]
            if config["Debug"]:
                logger.debug(latest_message)
            if latest_message.response_metadata and latest_message.content:
                yield latest_message.content.strip() + '\n'


if __name__ == '__main__':
    
    checkpoint = None
    session_config = {
        "configurable":{
            "thread_id": "1"
        }
    }
    
    if config["history"]["type"] == "InMemoryHistory":
        checkpoint = InMemorySaver()
        
    agent = ReactAgent(checkpoint)
    
    while True:
        inputs = input("> ")
        if inputs == "exit":
            break
        for chunk in agent.excute_stream(inputs, session_config):
            print(chunk, end= "", flush= True)