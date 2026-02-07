from utils.config_ import config
from langchain_core.prompts import PromptTemplate
from models.factory import OllamaChatModel
from utils.prompt_loader import load_prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from utils.logger import get_logger
from rag.vector_service import VectorStoreService

logger = get_logger("Rag")

class RagSummaryService:
    def __init__(self):
        super().__init__()
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.model = OllamaChatModel().generator(config["models"]["rag_summary"])
        self.prompt = load_prompt(config["prompts"]["rag_summary_prompt"])
        self.prompt_template = PromptTemplate.from_template(self.prompt)
        self.output_parser = StrOutputParser()
        self.chain = self.prompt_template | self.model | self.output_parser
        
    def retriever_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def excute(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        context = ""
        
        for idx, doc in enumerate(context_docs):
            context += f"【参考资料{idx + 1}】{doc.page_content} | 元数据: {doc.metadata} \n"
            
        return self.chain.invoke({
            "input": query,
            "context": context
        })
        
    def excute_for_emoji(self, query: str) -> str:
        context_docs = self.retriever_docs(query)
        context = "可选颜表情(如果没有可选，可以自由发挥)：\n"

        for doc in context_docs:
            context += f"{doc.page_content}\n"
            
        return context