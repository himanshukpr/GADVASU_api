# GADVASU Dairy Farming API

A scalable Flask-based REST API for a dairy farming advisory chatbot powered by LangChain and Ollama. The system uses RAG (Retrieval-Augmented Generation) to provide accurate, context-aware answers from dairy farming documentation.

## Features

- 🤖 **AI-Powered Chatbot** - Dairy farming advisory using Ollama LLM
- 📚 **RAG Architecture** - Context-aware responses from DOCX documents
- 🔍 **FAISS Vector Search** - Efficient semantic search
- 🏗️ **Modular Architecture** - Clean separation of concerns
- 🔧 **Environment-Based Config** - Easy deployment across environments
- 📊 **Structured Logging** - Comprehensive logging for debugging
- ✅ **Error Handling** - Robust exception handling
- 🧪 **Testing Ready** - Built with testing infrastructure

## Project Structure

```
GADVASU_api/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/                  # API endpoints
│   │   ├── health.py            # Health check
│   │   └── chat.py              # Chat & index rebuild
│   ├── services/                # Business logic
│   │   ├── vector_service.py    # FAISS vectorstore
│   │   └── chat_service.py      # LangChain RAG
│   ├── models/                  # Data models
│   │   └── schemas.py           # Pydantic schemas
│   ├── core/                    # Core configuration
│   │   ├── config.py            # App configuration
│   │   ├── constants.py         # Constants
│   │   └── exceptions.py        # Custom exceptions
│   └── utils/                   # Utilities
│       ├── logger.py            # Logging setup
│       └── helpers.py           # Helper functions
├── data/                        # DOCX documents
├── tests/                       # Test suite
├── run.py                       # Application entry point
├── requirements.txt             # Dependencies
└── .env                         # Environment variables
```

## Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed and running
- Required Ollama models:
  ```bash
  ollama pull llama3.2:1b
  ollama pull nomic-embed-text
  ```

### Installation

1. **Clone the repository**
   ```bash
   cd GADVASU_api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # .env file is already created with defaults
   # Edit if needed for your setup
   ```

5. **Add your documents**
   - Place DOCX files in the `data/` directory

### Running the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "ok",
  "message": "Chatbot backend running"
}
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "query": "What is mastitis in dairy cattle?"
}
```

**Response:**
```json
{
  "answer": "• Mastitis is an inflammation of the mammary gland...\n• Common causes include bacterial infections...\n• Treatment involves..."
}
```

### Rebuild Index
```http
POST /rebuild_index
```

**Response:**
```json
{
  "message": "Index rebuilt from DOCX files"
}
```

## Configuration

Edit `.env` file to customize:

```bash
# Flask Configuration
FLASK_ENV=development
PORT=5000

# AI Models
CHAT_MODEL=llama3.2:1b
EMBED_MODEL=nomic-embed-text

# LangChain Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVER_K=4

# Logging
LOG_LEVEL=DEBUG
```

## Development

### Running Tests
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_routes.py -v
```

### Code Formatting
```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/
```

## Deployment

### Production Settings

1. Update `.env`:
   ```bash
   FLASK_ENV=production
   SECRET_KEY=<strong-secret-key>
   LOG_LEVEL=WARNING
   ```

2. Use a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
   ```

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

## Integration with React Native Frontend

The API is designed to work seamlessly with the React Native frontend:

```javascript
// Example React Native integration
const chatWithBot = async (query) => {
  const response = await fetch('http://your-api-url:5000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  
  const data = await response.json();
  return data.answer;
};
```

## Architecture Benefits

### Scalability
- **Service Layer** - Easy to add new AI models or data sources
- **Blueprint Pattern** - Simple to add new API endpoints
- **Config Management** - Environment-based settings

### Maintainability
- **Separation of Concerns** - Clear module responsibilities
- **Type Validation** - Pydantic schemas ensure data integrity
- **Logging** - Comprehensive logging for debugging

### Team Collaboration
- **Modular Design** - Multiple developers can work independently
- **Clear Structure** - Easy onboarding for new team members
- **Testing Infrastructure** - Confidence in code changes

## Troubleshooting

### Ollama Connection Issues
```bash
# Check Ollama is running
ollama list

# Check Ollama service
curl http://localhost:11434/api/tags
```

### Index Build Failures
- Ensure DOCX files are in `data/` directory
- Check file permissions
- Verify Ollama embedding model is available

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black .`
6. Submit a pull request

## License

[Your License Here]

## Contact

For questions or support, please contact [Your Contact Info]
