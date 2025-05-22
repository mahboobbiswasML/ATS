from langchain.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

def build_vector_store(resume_texts):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    docs = []
    for text in resume_texts:
        docs.extend(splitter.create_documents([text]))
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = FAISS.from_documents(docs, embeddings)
    return db

def create_chatbot(db):
    qa_prompt = PromptTemplate(
        template="""
        You are an AI resume assistant. Answer questions based on the uploaded resumes.
        Be precise and provide relevant details from the resumes when possible.
        
        Context: {context}
        
        Question: {question}
        
        Answer:
        """,
        input_variables=["context", "question"]
    )
    
    retriever = db.as_retriever(search_kwargs={"k": 3})
    llm = Ollama(model="llama2")
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": qa_prompt}
    )
    return qa_chain