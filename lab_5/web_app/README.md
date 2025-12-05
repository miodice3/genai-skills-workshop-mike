# Lab 5 Web Application

A web-based chat interface for the Google GenAI agent with RAG and weather tools.

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Authenticate with Google Cloud
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# Start backend
python run.py
```

Backend will run at http://localhost:8000

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend

# Start simple HTTP server
python -m http.server 8080
```

Frontend will be available at http://localhost:8080

## Project Structure

```
lab_5/web_app/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── agent/       # Agent logic (core, weather, model_armor)
│   │   ├── routers/     # API endpoints (chat, health)
│   │   ├── config.py    # Configuration management
│   │   ├── models.py    # Pydantic models
│   │   └── main.py      # FastAPI application
│   ├── run.py           # Development server
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment template
│   └── README.md        # Backend documentation
└── frontend/            # Plain HTML/CSS/JS frontend
    ├── css/
    │   └── styles.css   # Styling
    ├── js/
    │   └── app.js       # Application logic
    ├── index.html       # Main page
    └── README.md        # Frontend documentation
```

## Features

- **Weather Queries**: Get current forecasts for any US city/state
- **RAG Knowledge Base**: Ask about the Alaska Department of Snow
- **Safety Validation**: All prompts and responses checked with Model Armor
- **Clean UI**: Modern chat interface with loading states and error handling
- **Real-time**: REST API communication with instant responses

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Google GenAI SDK (Gemini 2.5 Pro)
- Vertex AI RAG (knowledge retrieval)
- Google Maps API (geocoding)
- NOAA API (weather data)
- Model Armor (content safety)

**Frontend:**
- Plain HTML5
- CSS3 (no frameworks)
- Vanilla JavaScript (ES6+)
- Fetch API for HTTP requests

## Documentation

- **Backend**: See [backend/README.md](backend/README.md) for detailed setup, API docs, and troubleshooting
- **Frontend**: See [frontend/README.md](frontend/README.md) for usage, configuration, and customization

## Requirements

- Python 3.10+
- Google Cloud Project with Vertex AI and Model Armor enabled
- Google Maps API key
- Modern web browser

## Usage Examples

**Weather:**
```
What's the weather in Denver, CO?
Tell me the forecast for Miami, FL
```

**Alaska Department of Snow:**
```
What is the Alaska Department of Snow?
Can you tell me about snow in Alaska?
```

## Development Notes

- This is a local demo application - not production-ready
- No conversation history persistence (stateless)
- CORS configured for localhost only
- No authentication/authorization
- Environment variables manage all configuration

## Troubleshooting

**Backend won't start:**
- Check `.env` file has all required variables
- Verify `gcloud auth application-default login` was run
- Ensure virtual environment is activated

**Frontend can't connect:**
- Verify backend is running at http://localhost:8000
- Check browser console for CORS errors
- Ensure using HTTP server (not opening index.html directly)

**Model Armor blocks everything:**
- Verify template IDs in `.env` match your GCP project
- Check Model Armor configuration in Google Cloud Console

For detailed troubleshooting, see the README files in backend/ and frontend/ directories.

## License

This is a demo/educational project for Lab 5 of the GenAI Skills Workshop.
