from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from utils.logger import get_logger

logger = get_logger("Models")

class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self, model_name: str) -> BaseChatModel | Embeddings:
        pass
    
class OllamaEmbedModel(BaseModelFactory):
    def generator(self, model_name: str) -> Embeddings:
        try:
            model = OllamaEmbeddings(model= model_name)
            logger.info(f"模型 {model_name} 加载成功")
            return model
        except Exception as e:
            logger.error(f"模型 {model_name} 加载失败: {str(e)}")
            raise e

class OllamaChatModel(BaseModelFactory):
    def generator(self, model_name: str) -> BaseChatModel:
        try:
            model = ChatOllama(model= model_name)
            logger.info(f"模型 {model_name} 加载成功")
            return model
        except Exception as e:
            logger.error(f"模型 {model_name} 加载失败: {str(e)}")
            raise e