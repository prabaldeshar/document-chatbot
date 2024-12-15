import bs4
from langchain import hub
from langchain_community.vectorstores import Chroma 
from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class RAGService:

    def generate_response(self, question: str, text: str):
        # Create a Document object with the provided text
        from langchain_core.documents import Document
        docs = [Document(page_content=text)]
        
        retriever = self.get_retriever(docs)
        rag_chain = self.get_rag_chain(retriever)
        answer = rag_chain.invoke(question)
        self.delete_vectorstore()
        return answer
    
    def get_retriever(self, docs):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="rag_db")
        return vectorstore.as_retriever()
    
    def get_rag_chain(self, retriever):
        prompt = hub.pull("rlm/rag-prompt")
        llm = ChatOpenAI(model="gpt-4o-mini")

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain
    
    def delete_vectorstore(self):
        vectorstore = Chroma(persist_directory="rag_db")
        vectorstore.delete_collection()
        vectorstore.persist()