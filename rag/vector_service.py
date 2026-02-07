from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file import txt_loader, pdf_loader, csv_loader, get_file_md5_hex, listdir_with_allowed
from utils.logger import get_logger
from utils.config_ import config
from models.factory import OllamaEmbedModel
import os

logger = get_logger("Rag")

class VectorStoreService:
    def __init__(self):
        super().__init__()
        try:
            self.vector_store = Chroma(
                collection_name= config["vector_store"]["collection_name"],
                embedding_function= OllamaEmbedModel().generator(config["models"]["embed_model"]),
                persist_directory= config["vector_store"]["persist_directory"],
            )
            logger.info("成功加载向量数据库")
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size= config["vector_store"]["chunk_size"],
                chunk_overlap= config["vector_store"]["chunk_overlap"],
                separators= config["vector_store"]["separators"],
                length_function= len
            )
            logger.info("成功加载文档切片器")
        except Exception as e:
            logger.error(f"RagService初始化失败, 原因: {str(e)}")
            raise e
    
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": config["vector_store"]["k"]})
    
    def load_documents(self):
        file = config["vector_store"]["md5_file"]
        def check_md5(md5: str) -> bool:
            if not os.path.exists(file):
                open(file, "w", encoding= "utf-8")
                if config["debug"]:
                    logger.debug("未发现已存在的MD5文件，已重新创建MD5文件")
                return False
            
            with open(file, "r", encoding= "utf-8") as f:
                for line in f.readlines():
                    if line.strip() == md5:
                        logger.info("已存在相同MD5文件，无需加入向量数据库")
                        return True
            return False
        
        def save_md5(md5: str):
            try:
                with open(file, "a", encoding= "utf-8") as f:
                    f.write(md5 + "\n")
                if config["debug"]:
                    logger.debug("已保存MD5文件, 值为: {md5}")
            except Exception as e:
                logger.error(f"保存MD5文件失败, 值为: {md5}, 原因: {str(e)}")
                
        def get_file_documents(read_path: str) -> list:
            if read_path.endswith("txt"):
                return txt_loader(read_path)
            
            if read_path.endswith("pdf"):
                return pdf_loader(read_path)
            
            if read_path.endswith("csv"):
                return csv_loader(read_path)

            return []

        allowed_files = listdir_with_allowed(config["vector_store"]["data"], allowed_types= config["vector_store"]["allowed_types"])
        
        if not allowed_files:
            logger.info("未找到任何资料文件")
            return
        else:
            for filepath in allowed_files:
                md5_hex = get_file_md5_hex(filepath)
                if not md5_hex:
                    logger.error("获取文件MD5失败")
                    continue
                else:
                    try:
                        if check_md5(md5_hex):
                            logger.info(f"已存在相同MD5文件: {filepath}，跳过向量库存储")
                            continue
                        else:
                            documents_origin = get_file_documents(filepath)
                            documents = self.splitter.split_documents(documents_origin)
                            logger.info(f"加载文件 {filepath} 成功, 共 {len(documents)} 条数据")
                            if not documents:
                                logger.warning(f"文件 {filepath} 无有效文本")
                                continue
                            self.vector_store.add_documents(documents)
                            save_md5(md5_hex)
                            logger.info(f"{filepath}成功存储到向量数据库")
                    except Exception as e:
                        logger.error(f"向量数据库存储文件 {filepath} 失败, 错误信息: {str(e)}")
                        continue