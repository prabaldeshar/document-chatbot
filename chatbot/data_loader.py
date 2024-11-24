from abc import ABC, abstractmethod
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

import tempfile
import os


class DataLoader(ABC):
    """Abstract base class for document loaders"""
    @abstractmethod
    def load(self, file_obj):
        """Load content from file object"""
        pass

class PDFDataLoader(DataLoader):
    def load(self, file_obj):
        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
        
        try:
            # Pass the temporary file path to PyPDFLoader
            loader = PyPDFLoader(temp_file.name)
            pages = loader.load()
            return '\n'.join([page.page_content for page in pages])
        finally:
            # Clean up temporary file
            os.unlink(temp_file.name)

class DocxDataLoader(DataLoader):
    def load(self, file_obj):
        # Save DOCX to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
        
        try:
            # Pass the temporary file path to Docx2txtLoader
            loader = Docx2txtLoader(temp_file.name)
            pages = loader.load()
            return '\n'.join([page.page_content for page in pages])
        finally:
            # Clean up temporary file
            os.unlink(temp_file.name)

class TxtDataLoader(DataLoader):
    def load(self, file_obj):
        return file_obj.read().decode('utf-8')

# Factory to get the appropriate loader
def get_data_loader(file_extension):
    loaders = {
        'pdf': PDFDataLoader,
        'docx': DocxDataLoader,
        'txt': TxtDataLoader
    }
    loader_class = loaders.get(file_extension.lower())
    if not loader_class:
        raise ValueError(f'Unsupported file type: {file_extension}')
    return loader_class()
