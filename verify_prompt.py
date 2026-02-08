from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

model = ChatOllama(model= "qwen3:4b")

with open("./prompts/main_prompt.md", "r", encoding= "utf-8") as f:
    prompt = f.read()

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}")
    ]
)

chain = prompt_template | model | StrOutputParser()

memory = InMemoryChatMessageHistory()

def get_history(session_id):
    return memory

conversation_chain = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key= "input",
    history_messages_key= "history"
)

session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}

while True:
    inputs = input(">")
    if inputs == "exit":
        break
    for chunk in conversation_chain.stream({"input": inputs}, session_config):  # pyright: ignore[reportArgumentType]
        print(chunk, end= "", flush= True)
    print("\n")