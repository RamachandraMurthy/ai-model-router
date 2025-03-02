import random
import os
from fastapi import HTTPException, Header, Request
from loguru import logger
import time
import openai
from anthropic import Anthropic
import google.generativeai as genai
from typing import Dict, Any, Optional

from config import API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY

# Configure API clients
openai.api_key = OPENAI_API_KEY
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# ----- Multi-Model Selection & Real LLM API Calls -----

def select_llm_model(prompt: str) -> str:
    """
    Select the best model based on the prompt content.
    This is a simple implementation - in production you would use more sophisticated logic.
    """
    # Simple keyword-based routing
    prompt_lower = prompt.lower()
    
    # Check for specific capabilities in the prompt
    if "code" in prompt_lower or "programming" in prompt_lower or "function" in prompt_lower:
        return "OpenAI"  # OpenAI models are strong at code
    elif "creative" in prompt_lower or "story" in prompt_lower or "write" in prompt_lower:
        return "Anthropic"  # Anthropic models are strong at creative writing
    elif "research" in prompt_lower or "explain" in prompt_lower or "information" in prompt_lower:
        return "Google"  # Google models are strong at knowledge tasks
    
    # Default to OpenAI if no specific pattern is detected
    return "OpenAI"

def call_llm_api(model: str, prompt: str) -> dict:
    """
    Call the appropriate LLM API based on the selected model.
    Returns a dictionary with the response, tokens used, and cost.
    """
    try:
        if model == "OpenAI":
            return call_openai_api(prompt)
        elif model == "Anthropic":
            return call_anthropic_api(prompt)
        elif model == "Google":
            return call_google_api(prompt)
        else:
            # Fallback to OpenAI if model not recognized
            logger.warning(f"Unrecognized model {model}, falling back to OpenAI")
            return call_openai_api(prompt)
    except Exception as e:
        logger.error(f"Error calling {model} API: {str(e)}")
        # Return error message but don't fail completely
        return {
            "response": f"Error processing request with {model}: {str(e)}",
            "tokens_used": 0,
            "cost": 0
        }

def call_openai_api(prompt: str) -> dict:
    """Call OpenAI API with the given prompt."""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    # Extract response text
    response_text = response.choices[0].message.content
    
    # Calculate tokens and cost
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    
    # OpenAI pricing (as of my knowledge cutoff - adjust as needed)
    cost = (prompt_tokens * 0.0000015) + (completion_tokens * 0.000002)
    
    logger.info(f"OpenAI API: tokens {total_tokens}, cost ${cost:.6f}")
    return {
        "response": response_text,
        "tokens_used": total_tokens,
        "cost": cost
    }

def call_anthropic_api(prompt: str) -> dict:
    """Call Anthropic API with the given prompt."""
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract response text
    response_text = response.content[0].text
    
    # Calculate tokens (Anthropic doesn't return token counts in the same way)
    # This is an approximation
    input_tokens = len(prompt.split()) * 1.3  # rough approximation
    output_tokens = len(response_text.split()) * 1.3  # rough approximation
    total_tokens = input_tokens + output_tokens
    
    # Anthropic pricing (approximate - adjust as needed)
    cost = (input_tokens * 0.0000025) + (output_tokens * 0.0000075)
    
    logger.info(f"Anthropic API: approx tokens {int(total_tokens)}, cost ${cost:.6f}")
    return {
        "response": response_text,
        "tokens_used": int(total_tokens),
        "cost": cost
    }

def call_google_api(prompt: str) -> dict:
    """Call Google Gemini API with the given prompt."""
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    # Extract response text
    response_text = response.text
    
    # Google doesn't provide token counts directly
    # This is an approximation
    total_tokens = (len(prompt.split()) + len(response_text.split())) * 1.3
    
    # Google pricing (approximate - adjust as needed)
    cost = total_tokens * 0.000001  # $0.001 per 1000 tokens (approximate)
    
    logger.info(f"Google API: approx tokens {int(total_tokens)}, cost ${cost:.6f}")
    return {
        "response": response_text,
        "tokens_used": int(total_tokens),
        "cost": cost
    }

# ----- API Key Verification -----

def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return True

# ----- Simple In-Memory Rate Limiter -----

rate_limit_storage = {}

def rate_limiter(request: Request, limit: int = 10, timeframe: int = 60):
    client_ip = request.client.host
    current_time = time.time()
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    # Keep only timestamps within the timeframe.
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip]
        if current_time - timestamp < timeframe
    ]
    if len(rate_limit_storage[client_ip]) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limit_storage[client_ip].append(current_time)
