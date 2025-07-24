# SOVREN AI API Services

Production-ready API services for the SOVREN AI platform, optimized for B200 bare metal deployment.

## Services

### Data Ingestion Service (Port 8007)
High-throughput document processing and data pipeline with support for:
- File uploads (text, CSV, JSON, XML, PDF, Excel, Word)
- Streaming data ingestion
- Batch data processing
- URL content ingestion

### RAG Service (Port 8006)
B200-accelerated knowledge retrieval with:
- Vector similarity search
- Document indexing and chunking
- Retrieval-augmented generation
- Multi-user knowledge bases

## Dependencies

### Required
- `numpy` - Core numerical operations

### Optional (for full functionality)
- `asyncpg` - PostgreSQL database connectivity
- `redis` - Caching and job queue
- `pandas` - Enhanced CSV/Excel processing
- `scikit-learn` - Advanced similarity metrics

## Installation

```bash
# Install core dependencies
pip install numpy

# Install optional dependencies for full functionality
pip install asyncpg redis pandas scikit-learn openpyxl

# Install system tools for document extraction (Ubuntu/Debian)
sudo apt-get install pdftotext antiword
```

## Configuration

Create `/mnt/yellow-mackerel-volume/sovren/config/sovren.conf`:

```ini
REDIS_HOST=localhost
REDIS_PORT=6379
DB_HOST=localhost
DB_PORT=5432
DB_USER=sovren
DB_PASS=Renegades1!
```

## Usage

### Start Data Ingestion Service
```bash
python api/data_ingestion.py
```

### Start RAG Service
```bash
python api/rag_service.py
```

## API Endpoints

### Data Ingestion Service (8007)

#### Health Check
```bash
curl http://localhost:8007/health
```

#### File Upload
```bash
curl -X POST http://localhost:8007/upload \
  -H "Content-Type: application/octet-stream" \
  -H "X-User-ID: user123" \
  -H "X-Filename: document.txt" \
  --data-binary @document.txt
```

#### Stream Data
```bash
curl -X POST http://localhost:8007/stream \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "stream_data": "data", "stream_type": "json_lines"}'
```

### RAG Service (8006)

#### Health Check
```bash
curl http://localhost:8006/health
```

#### Index Document
```bash
curl -X POST http://localhost:8006/index \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "document": {
      "title": "Sample Document",
      "content": "Document content here...",
      "type": "text"
    }
  }'
```

#### Search Knowledge Base
```bash
curl -X POST http://localhost:8006/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "What is the main topic?",
    "limit": 10
  }'
```

#### Generate Answer
```bash
curl -X POST http://localhost:8006/answer \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "What is the main topic?"
  }'
```

## Error Handling

The services include robust error handling:
- Graceful degradation when optional dependencies are missing
- Proper null safety checks
- Comprehensive logging
- Fallback mechanisms for failed operations

## Performance

- Optimized for B200 GPU acceleration
- Multi-threaded HTTP servers
- Async/await patterns for I/O operations
- Connection pooling for database operations
- Vectorized operations for similarity search

## Security

- Input validation and sanitization
- File size limits (500MB max)
- Content type validation
- User isolation in knowledge bases
- Secure configuration management

## Monitoring

- Structured logging to `/mnt/yellow-mackerel-volume/sovren/logs/`
- Health check endpoints
- Performance metrics
- Error tracking and reporting

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
The code includes:
- Type hints throughout
- Comprehensive error handling
- Production-ready logging
- Modular design for maintainability 