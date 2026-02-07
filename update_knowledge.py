from rag.vector_service import VectorStoreService
from utils.logger import get_logger

logger = get_logger("Rag")

vector_service = VectorStoreService()

try:
    vector_service.load_documents()
    logger.info("成功加载知识库")
except Exception as e:
    logger.error(f"加载知识库失败: {str(e)}")