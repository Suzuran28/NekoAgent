from langchain.agents import create_agent
from models.factory import OllamaChatModel
from utils.config_ import config
from utils.prompt_loader import load_prompt
from utils.logger import get_logger
from tools.tools import get_rag, get_weather, get_time, get_weather_by_city
from tools.middleware import monitor_tool_call, monitor_model

logger = get_logger("Agent")

class ReactAgent:
    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            model= OllamaChatModel().generator(config["models"]["chat_model"]),
            tools= [get_rag, get_time, get_weather, get_weather_by_city],
            middleware= [monitor_tool_call, monitor_model],
            checkpointer= None,
            system_prompt= load_prompt(config["prompts"]["system_prompt"]),
        )
        
    def excute_stream(self, inputs: str):
        stream = self.agent.stream(
            {
                "messages": [
                    {"role": "user", "content": inputs}
                ]
            },
            stream_mode= "values"
        )
        
        for chunk in stream:
            latest_message = chunk["messages"][-1]
            if config["Debug"]:
                logger.debug(latest_message)
            if latest_message.response_metadata and latest_message.content:
                yield latest_message.content.strip() + '\n'


if __name__ == '__main__':
    agent = ReactAgent()
    while True:
        inputs = input("> ")
        if inputs == "exit":
            break
        for chunk in agent.excute_stream(inputs):
            print(chunk, end= "", flush= True)