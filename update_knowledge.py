from rag.vector_service import VectorStoreService
from utils.logger import get_logger
from utils.config_ import config
import logging
import os

logger = get_logger("Rag", logging.INFO)
    
def clear_vector_store():
    file = config["vector_store"]["md5_file"]
    try:
        f = open(file, "w", encoding= "utf-8")
        f.close()
        logger.info(f"成功清空已保存的MD5文件 {file}")
        counter = 0
        for path in os.listdir(config["vector_store"]["persist_directory"]):
            try:
                path = os.path.join(config["vector_store"]["persist_directory"], path)
                os.remove(path)
                logger.info(f"成功删除向量数据库文件 {path}")
                couter += 1
            except Exception as e:
                logger.warning(f"删除向量数据库文件 {path} 失败, 错误信息: {str(e)}")
                continue
        logger.info(f"清理完毕，共删除 {counter} 个文件")
    except Exception as e:
        logger.warning(f"清空向量数据库失败, 错误信息: {str(e)}")
        
def update_vector_store():
    try:
        vector_service = VectorStoreService()
        vector_service.load_documents()
        logger.info("成功加载知识库")
    except Exception as e:
        logger.error(f"加载知识库失败: {str(e)}")
    
if __name__ == '__main__':
    inputs = input("请选择操作：[1] 加载知识文件 [2] 删除所以已存在的知识 [其他] 退出\n> ")
    if inputs == "1":
        try:
            vector_service = VectorStoreService()            
            vector_service.load_documents()
            logger.info("成功加载知识库")
        except Exception as e:
            logger.error(f"加载知识库失败: {str(e)}")
    elif inputs == "2":
        try:
            clear_vector_store()
            logger.info(f"成功删除所有已存在的知识")
        except Exception as e:
            logger.error(f"删除所有已存在的知识失败: {str(e)}")