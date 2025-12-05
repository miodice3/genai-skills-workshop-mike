# Lab 5 Agent Backend

FastAPI backend for the Gemini Agent with Weather and RAG capabilities.

## Prerequisites

- Python 3.10 or higher
- Google Cloud Project with:
  - Vertex AI API enabled
  - Model Armor API enabled
  - RAG corpus created
- Google Maps API key
- Google Cloud CLI (`gcloud`) installed

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required environment variables in `.env`:
- `GOOGLE_API_KEY` - Your Google Maps API key
- `PROJECT_ID` - Your GCP project ID
- `RAG_CORPUS` - Full path to your Vertex AI RAG corpus
- `MODEL_ARMOR_TEMPLATE_ID` - Model Armor template for prompt validation
- `MODEL_ARMOR_RESPONSE_TEMPLATE_ID` - Model Armor template for response validation

### 4. Set up Google Cloud authentication

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

This sets up Application Default Credentials for the backend to access Google Cloud services.

## Local Development

### Start the development server

```bash
python run.py
```

The API will be available at http://localhost:8000

### API Endpoints

#### POST /api/chat
Send a message to the agent.

**Request:**
```json
{
  "message": "What's the weather in Denver, CO?"
}
```

**Response (Success):**
```json
{
  "response": "Denver, CO forecast: Sunny, 75°F... #FORECAST",
  "blocked": false,
  "blocked_reason": null
}
```

**Response (Blocked):**
```json
{
  "response": null,
  "blocked": true,
  "blocked_reason": "Response was blocked by Model Armor for safety reasons"
}
```

#### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-04T10:30:00"
}
```

### API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

All configuration is done via environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Maps API key | Required |
| `PROJECT_ID` | GCP project ID | Required |
| `LOCATION` | GCP region | us-central1 |
| `MODEL_ARMOR_LOCATION` | Model Armor endpoint location | us |
| `MODEL_NAME` | Gemini model name | gemini-2.5-pro |
| `MODEL_ARMOR_TEMPLATE_ID` | Prompt validation template | lab-five-query-template |
| `MODEL_ARMOR_RESPONSE_TEMPLATE_ID` | Response validation template | ma-response-filter |
| `RAG_CORPUS` | RAG corpus resource path | Required |
| `NOAA_USER_AGENT` | User-Agent for NOAA API | WeatherChatbot/1.0 |
| `API_TIMEOUT` | Request timeout in seconds | 60 |
| `LOG_LEVEL` | Logging level | INFO |

## Agent Behavior

The agent is configured to:

1. **Answer weather queries**: Uses Google Maps API for geocoding and NOAA API for weather forecasts
2. **Answer Alaska Department of Snow questions**: Uses Vertex AI RAG for knowledge retrieval
3. **Enforce content rules**:
   - Only responds to weather/snow/ADS questions
   - Limits responses to 240 characters
   - Adds appropriate hashtags: #FORECAST, #ALASKA_DS, #USEANOTHERCHATBOT
4. **Safety validation**: All prompts and responses are checked with Model Armor

## Example Queries

**Weather:**
```
What's the weather in Miami, FL?
Tell me the forecast for Denver, CO
```

**Alaska Department of Snow:**
```
What is the Alaska Department of Snow?
Tell me about ADS
```

**Out of Scope (should be blocked or refused):**
```
How many players are in the NBA?
What is the capital of France?
```

## Troubleshooting

### "Model Armor Blocked Prompt"
Your prompt triggered a content filter. Check your Model Armor template configuration and ensure the prompt follows content guidelines.

### "NOAA API failed"
The National Weather Service API may be temporarily unavailable. Check:
- Your internet connection
- NOAA API status at https://api.weather.gov
- The NOAA_USER_AGENT is properly configured

### Authentication errors
Ensure you've run:
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### "RAG corpus not found"
Verify your `RAG_CORPUS` environment variable contains the full resource path:
```
projects/YOUR_PROJECT/locations/LOCATION/ragCorpora/CORPUS_ID
```

### Import errors
Make sure you've:
1. Activated the virtual environment
2. Installed all dependencies from requirements.txt
3. Are running from the backend directory

### Port already in use
If port 8000 is already in use, either:
- Stop the other service using port 8000
- Modify `run.py` to use a different port
- Update the frontend's `API_BASE_URL` to match the new port

## Development Notes

- The backend is stateless - no conversation history is stored
- Each request is independent
- CORS is configured for localhost development only
- All sensitive credentials should be in `.env` (not committed to git)
- Logging outputs to console with configurable level

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   ├── agent/
│   │   ├── core.py          # Main agent logic
│   │   ├── weather.py       # Weather tools
│   │   └── model_armor.py   # Safety validation
│   └── routers/
│       ├── chat.py          # Chat endpoint
│       └── health.py        # Health check
├── run.py                   # Dev server launcher
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```
