# AI Model Router

An intelligent system that routes user prompts to the most appropriate AI model (OpenAI, Anthropic, or Google) based on the content of the query.

## Project Overview

This application consists of a FastAPI backend and a React frontend. It analyzes user prompts and selects the most suitable AI model to handle the request, then returns the response with usage metrics.

### Key Features

- **Intelligent Model Selection**: Routes queries to OpenAI, Anthropic (Claude), or Google (Gemini) based on content analysis
- **Real API Integration**: Connects to actual AI model APIs
- **Cost Tracking**: Calculates and displays token usage and cost for each response
- **Real-time Logging**: WebSocket connection for displaying system logs
- **Database Storage**: Stores chat history and analytics

## Technical Stack

### Backend
- FastAPI
- SQLite (for development)
- WebSockets
- Celery (for async tasks)

### Frontend
- React
- WebSocket client

## Required API Keys

To run the application, you need to set these environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `GOOGLE_API_KEY` - Your Google AI API key

## How to Run

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Model Selection Logic

The system currently uses keyword-based routing:
- Code-related queries → OpenAI
- Creative writing → Anthropic
- Research and explanations → Google

This can be extended with more sophisticated routing logic in the future. 