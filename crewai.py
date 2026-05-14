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

# Example task
task = Task(
    description="Answer the user's question using available tools.",
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

if __name__ == "__main__":
    result = crew.kickoff(inputs={"user_input": "What is 2 + 2?"})
    print(result)
