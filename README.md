# Document Chatbot Backend

A Django-based REST API that allows users to upload documents (PDF, DOCX, TXT) and ask questions about their content using OpenAI's GPT models.

## Prerequisites

- Docker
- Docker Compose
- Git

## Project Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/prabaldeshar/document-chatbot.git
   cd document-chatbot
   ```

2. **Environment Setup**
   - Create a `.env` file in the root directory (optional)
   ```env
   OPENAI_API_KEY=<Your OpenAI API Key>
   ```

3. **Build and Run the Project**
   ```bash
   # Remove any existing containers and volumes
   docker compose down -v

   # Build and start the services
   docker compose up --build
   ```

## Project Structure

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
├── document_chatbot/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── chatbot/
    ├── models.py
    ├── views.py
    ├── data_loader.py
    └── rag_service.py
```

## Available Commands

- **Start the project**
  ```bash
  docker compose up
  ```

- **Start in detached mode**
  ```bash
  docker compose up -d
  ```

- **Stop the project**
  ```bash
  docker compose down
  ```

- **View logs**
  ```bash
  docker compose logs
  ```

- **Access Django shell**
  ```bash
  docker compose exec web python manage.py shell
  ```

## Accessing the Application

- Django application: http://localhost:8000
- Admin interface: http://localhost:8000/admin



## API Endpoints

### 1. Upload Document
Upload a document for processing.

- **URL**: `/api/upload/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

**Request Body**:
```
{
    "file": <file_object>  // PDF, DOCX, or TXT file
}
```

**Success Response** (201 Created):
```json
{
    "status": 1,
    "message": "Document uploaded successfully",
    "details": {
        "id": 1,
        "file": "/media/documents/example.pdf",
        "name": "example.pdf",
        "uploaded_at": "2024-03-21T10:00:00Z"
    }
}
```

**Error Response** (400 Bad Request):
```json
{
    "status": 0,
    "message": "No file provided",
    "details": {}
}
```

### 2. Ask Question
Ask a question about an uploaded document.
- **URL**: `/api/ask/`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Request Body**:
```json
{
    "document_id": 1,
    "question": "What is the main topic of this document?"
}
```

**Success Response** (200 OK):
```json
{
    "status": 1,
    "message": "Question answered successfully",
    "details": {
        "question": "What is the main topic of this document?",
        "answer": "The document discusses...",
        "document_name": "example.pdf",
        "session_id": "doc_1"
    }
}
```

**Error Response** (404 Not Found):
```json
{
    "status": 0,
    "message": "Document not found",
    "details": {}
}
```


## Usage Examples

### Using cURL

1. **Upload a Document**
```bash
curl -X POST \
  -F "file=@/path/to/your/document.pdf" \
  http://localhost:8000/api/upload/
```

2. **Ask a Question**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "question": "What is this document about?"}' \
  http://localhost:8000/api/ask/
```