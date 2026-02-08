from langgraph.checkpoint.postgres import PostgresSaver
from utils.config_ import config
from utils.logger import get_logger
import os

logger = get_logger("History")

def get_DB_URL():
    username = config["postgres"]["username"]
    if username == "None":
        username = os.getenv("POSTGRES_USERNAME")
        if not username:
            logger.error("未能读取到username")
            raise Exception("未能读取到username")
        
    password = config["postgres"]["password"]
    if password == "None":
        password = os.getenv("POSTGRES_PASSWORD")
        if not password:
            logger.error("未能读取到password")
            raise Exception("未能读取到password")

    HOST = config["postgres"]["host"]

    DB_NAME = config["postgres"]["db_name"]

    PORT = config["postgres"]["port"]

    DB_URL = f"postgresql://{username}:{password}@{HOST}:{PORT}/{DB_NAME}?sslmode=disable"

    if config["Debug"]:
        logger.debug(f"[Postgres] {DB_URL}")
    
    return DB_URL