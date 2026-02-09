# AI Coding Agent Backend

A production-ready FastAPI backend for streaming AI chat interactions using the DeepSeek model via OpenRouter API. Built with proper error handling, structured logging, and configuration management.

## Features

✨ **Streaming Chat API** - Real-time streaming responses using Server-Sent Events (SSE)  
🔐 **Secure Authentication** - API key-based authentication  
💾 **Session Memory** - Conversation history management per session  
📝 **Structured Logging** - Colored console logs with timestamps  
⚙️ **Environment Configuration** - Centralized config with validation  
🛡️ **Error Handling** - Custom exceptions for better debugging  
🔄 **CORS Support** - Configurable cross-origin requests  
📦 **Pinned Dependencies** - Reproducible builds with version constraints

## Architecture

```
ai-coding-agent-backend/
├── agent/                  # Agent implementations
│   ├── __init__.py
│   └── deepseek.py        # DeepSeek streaming agent
├── core/                  # Core utilities (legacy)
│   └── memory.py          # Short-term memory management
├── src/
│   └── core/              # New core modules
│       ├── config.py      # Configuration management
│       ├── logger.py      # Structured logging
│       └── exceptions.py  # Custom exceptions
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Prerequisites

- Python 3.10+
- OpenRouter API Key ([Get one here](https://openrouter.ai/keys))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/1mVivek/ai-coding-agent-backend.git
cd ai-coding-agent-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required: Get from https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Required: Generate a secure random string
INTERNAL_API_KEY=your_internal_api_key_here

# Optional: Logging level
LOG_LEVEL=INFO
```

**Generate a secure API key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Usage

### Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at: `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model": "deepseek/deepseek-chat",
  "version": "1.0.0"
}
```

#### Chat (Streaming)
```bash
POST /chat
Headers:
  x-api-key: your_internal_api_key
  Content-Type: application/json

Body:
{
  "message": "Hello, can you help me with Python?",
  "session_id": "optional-session-id"
}
```

Response (Server-Sent Events):
```
data: Hello
data: !
data:  I'd
data:  be
data:  happy
data:  to
data:  help
...
event: done
data: [DONE]
```

### Example with cURL

```bash
curl -X POST http://localhost:8000/chat \
  -H "x-api-key: your_internal_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain async/await in Python",
    "session_id": "test-session-1"
  }' \
  --no-buffer
```

### Example with Python

```python
import httpx
import asyncio

async def chat_stream():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/chat",
            headers={"x-api-key": "your_internal_api_key"},
            json={"message": "Hello!", "session_id": "test-1"},
            timeout=None,
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    print(line[6:], end="", flush=True)

asyncio.run(chat_stream())
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | OpenRouter API key |
| `INTERNAL_API_KEY` | Yes | - | Internal authentication key |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `MODEL_NAME` | No | deepseek/deepseek-chat | Model to use |
| `MODEL_TEMPERATURE` | No | 0.2 | Model temperature (0-2) |
| `MODEL_MAX_TOKENS` | No | 2000 | Max tokens per response |
| `OPENROUTER_API_URL` | No | https://openrouter.ai/api/v1/chat/completions | API endpoint |
| `CORS_ORIGINS` | No | localhost:5173, aura-frontend | Allowed origins |

### Model Configuration

You can override model parameters per request or via environment:

```python
# Via environment
MODEL_TEMPERATURE=0.5
MODEL_MAX_TOKENS=4000

# Or programmatically in agent/deepseek.py
await stream_agent(messages, temperature=0.5, max_tokens=4000)
```

## Deployment

### Deploy to Render

1. Fork this repository
2. Create a new Web Service on [Render](https://render.com)
3. Connect your forked repository
4. Configure environment variables in Render dashboard
5. Deploy!

Render will use the `Procfile` automatically.

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Click the button above
2. Add environment variables
3. Deploy!

### Deploy with Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t ai-agent-backend .
docker run -p 8000:8000 --env-file .env ai-agent-backend
```

## Development

### Code Structure

- **`agent/deepseek.py`** - Core streaming logic with proper error handling
- **`src/core/config.py`** - Environment validation using Pydantic
- **`src/core/logger.py`** - Structured logging with colors
- **`src/core/exceptions.py`** - Custom exception classes
- **`core/memory.py`** - Session memory management
- **`main.py`** - FastAPI app with endpoints

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Troubleshooting

### "OPENROUTER_API_KEY is not set"
- Make sure `.env` file exists and contains the key
- Verify the key is valid at https://openrouter.ai/keys

### "Unauthorized" error
- Check that `x-api-key` header matches `INTERNAL_API_KEY` in `.env`
- Header name must be exactly `x-api-key` (lowercase)

### Stream not working
- Ensure client supports Server-Sent Events (SSE)
- Disable buffering in your HTTP client
- Check CORS settings if calling from browser

### Import errors
- Run `pip install -r requirements.txt` to ensure all dependencies are installed
- Check Python version is 3.10+

## API Response Format

### Success Stream
```
data: Hello
data:  world
data: !
event: done
data: [DONE]
```

### Error Response
```
event: error
data: API Error: Rate limit exceeded
```

## Security Considerations

- Never commit `.env` file to version control
- Use strong, random API keys in production
- Enable HTTPS in production
- Rotate API keys regularly
- Validate all user inputs

## Performance

- Async/await for non-blocking I/O
- Streaming responses for real-time UX
- Connection pooling with httpx
- Configurable timeouts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [DeepSeek](https://www.deepseek.com/) via [OpenRouter](https://openrouter.ai/)
- Inspired by modern AI coding assistants