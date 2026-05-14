from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
import json

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
    allow_delegation=False
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
