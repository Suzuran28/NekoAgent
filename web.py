import streamlit as st
from utils.config_ import config
from agent import ReactAgent
from langgraph.checkpoint.memory import InMemorySaver
from utils.logger import get_logger
from time import sleep
import re

logger = get_logger("webUI")

inputs = st.chat_input("在此键入...", accept_file= "multiple", file_type= ["png", "jpg", "jpeg"])

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    msg = st.chat_message(message["role"])
    content = message["content"]
    img_files = re.findall(r"@'(.+?)'", content)
    msg.image(img_files, width= 200)
    msg.write((re.sub(r"@'(.+?)'", "", content)).replace("文件：", ""))

if "agent" not in st.session_state:
    if config["history"]["type"] == "None":
        agent = ReactAgent(None)
    
    elif config["history"]["type"] == "InMemoryHistory":
        checkpoint = InMemorySaver()
        agent = ReactAgent(checkpoint)
        
    st.session_state["agent"] = agent

session_config = {
    "configurable":{
        "thread_id": "Test01"
    }
}

if inputs:
    context = ""
    
    files = inputs.files
    if files:
        context += "文件："
    
    for idx, file in enumerate(files):
        with open(f"{config["file"]["inputs"]}/{file.name}", "wb") as f:
            f.write(file.getbuffer())
            context += f"@'{config["file"]["inputs"]}/{file.name}' "
            
    message = st.chat_message("user")
    if files:
        message.image([f"{config["file"]["inputs"]}/{file.name}" for file in files], width= 200)
    message.write(inputs.text)
    
    context += f"\n{inputs.text}"
    
    st.session_state["messages"].append({"role": "user", "content": context})
    
    logger.info(f"用户输入: {context}")
    
    def capture_stream(chunk):
        for char in chunk:
            yield char
            sleep(0.05)
    
    with st.spinner("思考中..."):
        res_list = []
        for chunk in st.session_state["agent"].excute_stream(context, session_config):
            res_list.append(chunk)
            st.chat_message("assistant").write_stream(capture_stream(chunk))
    st.session_state["messages"].append({"role": "assistant", "content": "".join(res_list)})        