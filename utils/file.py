import hashlib
from utils.logger import get_logger
import os
from utils.config_ import config
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader

logger = get_logger("Utils")

def get_file_md5_hex(file_path: str) -> str | None:
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return None
    if not os.path.isfile(file_path):
        logger.warning(f"不是文件: {file_path}")
        return None
    md5_obj = hashlib.md5()
    chunk_size = config["lazy_loading"]["chunk_size"]
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        md5_hex = md5_obj.hexdigest()
        logger.info(f"计算文件MD5成功: {file_path} 值为: {md5_hex}")
        return md5_hex
    except Exception as e:
        logger.error(f"计算文件MD5失败: {file_path}, 原因: {str(e)}")
        return None
    
def listdir_with_allowed(path: str, allowed_types: list[str]) -> list[str] | None:
    files = []
    
    if not os.path.exists(path):
        logger.error(f"目录不存在: {path}")
        return None
    
    if not os.path.isdir(path):
        logger.warning(f"不是目录: {path}")
        return None
    
    for file in os.listdir(path):
        if file.endswith(tuple(allowed_types)):
            files.append(os.path.join(path, file))
            
    if config["Debug"]:
        logger.debug(f"[listdir_with_allowed] files: {files}")
    
    return files

def pdf_loader(file_path: str, pwd: str | None = None) -> list[Document]:
    lists = []
    
    for doc in PyPDFLoader(file_path= file_path, password= pwd).lazy_load():
        lists.append(doc)
    
    if config["Debug"]:
        logger.debug(f"[pdfLoader] lists: {lists}")   
    
    return lists

def txt_loader(file_path: str) -> list[Document]:
    lists = []
    
    for doc in TextLoader(file_path= file_path, encoding= "utf-8").lazy_load():
        lists.append(doc)
    
    if config["Debug"]:
        logger.debug(f"[textLoader] lists: {lists}")
    
    return lists

def csv_loader(file_path: str) -> list[Document]:
    lists = []
    
    for doc in CSVLoader(file_path= file_path, encoding= "utf-8").lazy_load():
        lists.append(doc)
    
    if config["Debug"]:
        logger.debug(f"[csvLoader] lists: {lists}")
    
    return lists