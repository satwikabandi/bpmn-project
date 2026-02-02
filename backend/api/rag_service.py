from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

class RAGService:
    def __init__(self):
        self.vector_store_path = "faiss_index"
        # Using the same XLM-R model for consistency
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-xlm-r-multilingual-v1")
        self.vector_store = None

    def process_file(self, file_path):
        """
        Loads a PDF, splits it, and creates a FAISS index.
        """
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = text_splitter.split_documents(documents)
        
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)
        return len(texts)

    def retrieve_context(self, query):
        """
        Retrieves relevant context for a given query.
        """
        if not os.path.exists(self.vector_store_path):
            return ""
        
        if not self.vector_store:
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
            
        docs = self.vector_store.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])
