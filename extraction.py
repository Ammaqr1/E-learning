import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS,Chroma


class extraction_py:
    
        
    def get_pdf_text(self,pdf):
        all_text = ""
        with pdfplumber.open(pdf) as pdf:
            for page in pdf.pages:
                all_text += page.extract_text()
                
        return all_text 
    
    def get_text_chunks(self,text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)
        return chunks
    
    def get_vector_store_by_faiss(self,text_chunks):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")


    def get_vector_store_by_chroma(self,text_chunks):
        embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
        vectorstore = Chroma.from_texts(texts=text_chunks, 
                                    embedding=embeddings)
        
        return vectorstore




