import base64
import httpx
from PIL import Image
import io
from utils.logger import get_logger
from models.factory import OllamaChatModel
from utils.config_ import config
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from utils.prompt_loader import load_prompt

logger = get_logger("Utils")

def get_img_base64(inputs: str) -> str:
    if inputs.startswith("http"):
        logger.info(f"正在从链接 {inputs} 获取图片的 base64 编码")
        try:
            img_base64 = base64.b64encode(httpx.get(inputs).content).decode("utf-8")
            logger.info(f"获取图片的 base64 编码成功")
            if config["Debug"]:
                logger.debug(f"图片 {inputs} base64 : {img_base64}")
            return img_base64
        except Exception as e:
            logger.error(f"获取图片的 base64 编码失败, 错误信息: {str(e)}")
            return str(e)
    else:
        try:
            with Image.open(inputs) as img:
                logger.info(f"正在从文件 {inputs} 获取图片的 base64 编码")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_bytes = buffer.getvalue()
                img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                logger.info(f"获取图片的 base64 编码成功")
                if config["Debug"]:
                    logger.debug(f"图片 {inputs} base64 : {img_base64}")
                return img_base64
        except Exception as e:
            logger.error(f"获取图片的 base64 编码失败, 错误信息: {str(e)}")
            return str(e)
        
def get_description(base64: str) -> str:
    model = OllamaChatModel().generator(config["models"]["vision_model"])
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", load_prompt(config["prompts"]["vision_description_prompt"])),
        HumanMessage(
            content= [{
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64}"}
            }]
        )
    ])
    chain = prompt_template | model | StrOutputParser()
    try:
        response = chain.invoke({})
        logger.info(f"获取图片描述成功")
    except Exception as e:
        logger.error(f"获取图片描述失败, 错误信息: {str(e)}")
        return f"获取图片描述失败, 错误信息: {str(e)}"
    if config["Debug"]:
        logger.debug(f"图片描述: {response}")
    return response