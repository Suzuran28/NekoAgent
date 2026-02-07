from langchain_core.tools import tool
from rag.rag_summary import RagSummaryService
from utils.logger import get_logger
from utils.config_ import config
from datetime import datetime
import requests
import json

logger = get_logger("Tools")
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
)

@tool(description= "从向量存储库中检索参考资料，传入问题(str)，返回总结过的参考资料(str)")
def get_rag(query: str) -> str:
    rag = RagSummaryService()
    try:
        response = rag.excute(query)
        logger.info(f"成功执行向量检索")
        if config["debug"]:
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
        return "天气查询失败，请稍后再试"

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
        return "天气查询失败，请稍后再试"

@tool(description= "获取时间，不需要传入参数，返回当前时间(str)")
def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")