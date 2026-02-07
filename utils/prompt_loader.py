from utils.logger import get_logger
from utils.config_ import config
import os

logger = get_logger("Utils")

def load_prompt(prompt_file: str):
    prompt = ""
    try:
        chunk_size = config["lazy_loading"]["chunk_size"]
        with open(prompt_file, "r", encoding= "utf-8") as f:
            while chunk := f.read(chunk_size):
                prompt += chunk
        logger.info(f"成功加载提示词文件 {prompt_file}")
        return prompt
    except Exception as e:
        logger.error(f"提示词文件 {prompt_file} 加载失败, 原因: {str(e)}")
        raise e