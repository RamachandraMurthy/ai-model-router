# AI Model Router - Project Context

## Current State
The AI Model Router project has been set up and pushed to GitHub. The repository is available at: https://github.com/RamachandraMurthy/ai-model-router.git

## Project Overview
This is a real AI Model Router application that intelligently routes user prompts to the most appropriate AI model (OpenAI, Anthropic, or Google) based on the content of the query. The application consists of a FastAPI backend and a React frontend.

## Key Components

### Backend (FastAPI)
- **Model Selection Logic**: Routes queries to the appropriate AI model based on content analysis
- **Real API Integration**: Connects to OpenAI, Anthropic (Claude), and Google (Gemini) APIs
- **Database**: Uses SQLite for storing chat history and analytics
- **WebSocket**: Provides real-time logging capabilities
- **Authentication**: Uses API key authentication for security

### Frontend (React)
- **Modern UI**: Clean, responsive interface with proper message styling
- **Real-time Logs**: WebSocket connection for displaying logs
- **Cost Tracking**: Shows token usage and cost for each AI response

## Implementation Status
- All code has been updated to use real AI model APIs instead of simulations
- The backend is configured to use environment variables for API keys
- The frontend is styled with a modern, responsive design
- WebSocket authentication has been implemented

## Required API Keys
To run the application, you need to set these environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `GOOGLE_API_KEY` - Your Google AI API key

## How to Run the Application
### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm start
```

### Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Technical Details
- The model selection is based on keyword analysis in the prompt
- Token usage and cost calculations are implemented for all models
- Error handling is in place for API failures
- The application includes rate limiting for API calls

## Next Steps
Potential improvements and features to work on:
1. Enhance the model selection logic with more sophisticated algorithms
2. Add user authentication and multi-user support
3. Implement more detailed analytics and visualization
4. Add caching for improved performance
5. Enhance error handling and fallback mechanisms
6. Implement unit and integration tests

This is a fully functional implementation that connects to real AI services, not a simulation or mockup. 