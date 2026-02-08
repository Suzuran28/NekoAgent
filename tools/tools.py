from langchain_core.tools import tool
from rag.rag_summary import RagSummaryService
from utils.logger import get_logger
from utils.config_ import config
from datetime import datetime
import requests
import json
import os
from utils.img import get_img_base64, get_description

logger = get_logger("Tools")
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
)

@tool(description= "从向量库中寻找合适的颜表情，传入想表达的心情(str)，返回颜表情(str)")
def get_emoji(mood: str) -> str:
    rag = RagSummaryService()
    try:
        response = rag.excute_for_emoji(mood)
        logger.info(f"成功执行向量检索")
        if config["Debug"]:
            logger.debug(f"向量检索结果: {response}")
        return response
    except Exception as e:
        logger.error(f"向量检索失败, 原因: {str(e)}")
        raise e

@tool(description= "从向量存储库中检索参考资料，传入问题(str)，返回总结过的参考资料(str)")
def get_rag(query: str) -> str:
    rag = RagSummaryService()
    try:
        response = rag.excute(query)
        logger.info(f"成功执行向量检索")
        if config["Debug"]:
            logger.debug(f"向量检索结果: {response}")
        return response
    except Exception as e:
        logger.error(f"向量检索失败, 原因: {str(e)}")
        raise e
    
@tool(description= "获取城市天气，传入城市名称(str)，返回天气信息(str)")
def get_weather_by_city(city: str) -> str:
    try:
        response = session.get(f"https://uapis.cn/api/v1/misc/weather?city={city}")
        info = json.loads(response.text)
        logger.info(f"成功获取天气信息")
        context = f"{info['weather']}，{info['temperature']}摄氏度，{info['wind_direction']}，风力{info['wind_power']}级, 湿度{info['humidity']}%"
        return context
    except Exception as e:
        logger.error(f"获取天气信息失败, 错误信息: {str(e)}")
        return "天气查询失败"

@tool(description= "直接获取天气，不需要传入参数，返回天气信息(str)")
def get_weather() -> str:
    try:
        response = session.get("https://uapis.cn/api/v1/network/myip")
        info = json.loads(response.text)
        region = info["region"]
        response = session.get(f"https://uapis.cn/api/v1/misc/weather?city={region}")
        info = json.loads(response.text)
        logger.info(f"成功获取天气信息")
        context = f"{region}，{info['weather']}，{info['temperature']}摄氏度，{info['wind_direction']}，风力{info['wind_power']}级, 湿度{info['humidity']}%"
        return context
        
    except Exception as e:
        logger.error(f"获取天气信息失败, 错误信息: {str(e)}")
        return "天气查询失败"

@tool(description= "获取时间，不需要传入参数，返回当前时间(str)")
def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool(description= "能够获取文件夹详情，不需要传入参数，返回文件夹详情(str)")
def check_filelist() -> str:
    try:
        lists = os.listdir(config["file"]["inputs"])
        logger.info(f"成功获取文件夹列表")
        if config["Debug"]:
            logger.debug(f"文件夹列表: {lists}")
        return "\n".join(lists)
    except Exception as e:
        logger.error(f"获取文件夹列表失败, 错误信息: {str(e)}")
        return "获取文件夹列表失败"
    
@tool(description= "能够读取文件内容，传入文件名称(包括后缀名，str)，返回文件内容(str)")
def check_file(file_name: str) -> str:
    try:
        with open(os.path.join(config["file"]["inputs"], file_name), "r", encoding= "utf-8") as f:
            context = ""
            while chunk:= f.read(config["file"]["chunk_size"]):
                context += chunk
        logger.info(f"成功读取文件")
        if config["Debug"]:
            logger.debug(f"文件内容: {context} \n" + "*" * 100)
        return context
    except Exception as e:
        logger.warning(f"读取文件失败, 错误信息: {str(e)}")
        return f"读取文件失败，错误信息: {str(e)}"

@tool(description= "能够写入和新建文件，传入文件名称(包括后缀名，str)，文件内容(str)，返回写入结果(str)")
def modify_file(file_path: str, content: str) -> str:
    try:
        with open(os.path.join(config["file"]["outputs"], file_path), "w", encoding= "utf-8") as f:
            f.write(content)
        logger.info(f"成功写入文件")
        return "操作成功"
    except Exception as e:
        logger.warning(f"写入文件失败, 错误信息: {str(e)}")
        return f"操作失败，错误信息: {str(e)}"
    
@tool(description= "能够识别图片，传入图片名称(包括后缀名，str)或网址(str)，返回描述图片的内容(str)")
def read_img(inputs: str):
    img_base64 = get_img_base64(inputs)
    if img_base64 is None:
        return "获取图片base64失败，请检查输入是否正确"
    response = get_description(img_base64)
    return response