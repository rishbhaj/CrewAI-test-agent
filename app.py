from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure LLM
def get_llm_config():
    """Get LLM configuration from environment variables"""
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return {
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "api_key": api_key
        }
    
    elif llm_provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return {
            "provider": "anthropic",
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            "api_key": api_key
        }
    
    elif llm_provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        return {
            "provider": "groq",
            "model": os.getenv("GROQ_MODEL", "gemma-2-9b-it"),
            "api_key": api_key
        }
    
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

# Validate LLM configuration on startup
try:
    llm_config = get_llm_config()
except ValueError as e:
    print(f"Warning: LLM not configured - {str(e)}")
    print("Please set environment variables for your LLM provider before making requests")

# Define custom tools
@tool
def search_web(query: str) -> str:
    """Search the web for information about a query."""
    return f"Search results for: {query}"

@tool
def calculate(expression: str) -> str:
    """Perform mathematical calculations."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_current_date() -> str:
    """Get the current date and time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Create an agent with tools
agent = Agent(
    role="AI Assistant",
    goal="Help users by searching information, performing calculations, and providing current date/time",
    backstory="You are a helpful AI assistant with access to various tools to assist with user queries.",
    tools=[search_web, calculate, get_current_date],
    verbose=True,
    allow_delegation=False,
    llm=None  # Will be configured from environment variables
)

# FastAPI app
app = FastAPI(title="CrewAI Agent API", version="1.0.0")

# Request model
class QueryRequest(BaseModel):
    query: str

# Response model
class QueryResponse(BaseModel):
    query: str
    response: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "CrewAI Agent API is running"}

@app.post("/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    """
    Send a query to the CrewAI agent.
    
    Args:
        request: QueryRequest object with 'query' field
        
    Returns:
        QueryResponse with the query and agent's response
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Check if LLM is configured
        try:
            llm_config = get_llm_config()
        except ValueError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"LLM not configured: {str(e)}. Please set the appropriate environment variables."
            )
        
        # Create task for this specific query
        task = Task(
            description=request.query,
            agent=agent,
            expected_output="A helpful response using available tools when necessary."
        )
        
        # Create and run crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        result = crew.kickoff()
        
        return QueryResponse(
            query=request.query,
            response=str(result)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "CrewAI Agent API",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Health check"},
            {"path": "/ask", "method": "POST", "description": "Send query to agent"},
            {"path": "/health", "method": "GET", "description": "Detailed health check"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
