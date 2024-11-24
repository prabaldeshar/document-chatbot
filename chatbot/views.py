from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from chatbot.serializers import DocumentSerializer
from .models import Document
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.memory import ChatMessageHistory
import os
from dotenv import load_dotenv
from chatbot.rag_service import RAGService
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from chatbot.data_loader import get_data_loader

load_dotenv()

def create_response(success, message, details=None):
    """Helper function to create standardized response"""
    return {
        'status': 1 if success else 0,
        'message': message,
        'details': details or {}
    }

class DocumentProcessor:
    def __init__(self):
        self.vector_stores = {}
        
    def process_document(self, document_id, content):
        if document_id not in self.vector_stores:
            # Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50
            )
            splits = text_splitter.split_text(content)
            
            # Create embeddings and vector store
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.from_texts(splits, embeddings)
            
            self.vector_stores[document_id] = vector_store
            
        return self.vector_stores[document_id]

document_processor = DocumentProcessor()

# Store for chat histories
message_store = {}

def get_session_history(session_id: str):
    """Get or create message history for a session"""
    if session_id not in message_store:
        message_store[session_id] = ChatMessageHistory()
    return message_store[session_id]

# Create your views here.

@api_view(['POST'])
def upload_document(request):
    if 'file' not in request.FILES:
        return Response(
            create_response(
                success=False,
                message='No file provided'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file_obj = request.FILES['file']
    try:
        file_extension = file_obj.name.split('.')[-1].lower()
        loader = get_data_loader(file_extension)
        content = loader.load(file_obj)

        document = Document.objects.create(
            file=file_obj,
            name=file_obj.name,
            content=content
        )
        serializer = DocumentSerializer(document)
        return Response(
            create_response(
                success=True,
                message='Document uploaded successfully',
                details=serializer.data
            ),
            status=status.HTTP_201_CREATED
        )
    except UnicodeDecodeError:
        return Response(
            create_response(
                success=False,
                message='File must be a text document'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def ask_question(request):
    if not all(k in request.data for k in ['document_id', 'question']):
        return Response(
            create_response(
                success=False,
                message='document_id and question are required'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        document = Document.objects.get(id=request.data['document_id'])
        session_id = f"doc_{document.id}"
        
        # Initialize text splitter and create chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        content = document.content
        
        answer = RAGService().generate_response(request.data['question'], content)
        response_details = {
            'question': request.data['question'],
            'answer': answer,
            'document_name': document.name,
            'session_id': session_id
        }

        return Response(
            create_response(
                success=True,
                message='Question answered successfully',
                details=response_details
            )
        )
        
    except Document.DoesNotExist:
        return Response(
            create_response(
                success=False,
                message='Document not found'
            ),
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            create_response(
                success=False,
                message=f'Error processing question: {str(e)}'
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
