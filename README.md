# CrewAI Agent API

A FastAPI wrapper for your CrewAI agent that provides REST API endpoints for querying the agent.

## Features

- FastAPI REST API with async support
- CrewAI agent with multiple tools (search, calculate, current date)
- Health check endpoints
- Ready for deployment on Railway

## Local Development

### Prerequisites

- Python 3.10+
- pip or conda

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your LLM provider:
   - Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` and add your API key for your chosen LLM provider

3. Run the API locally:
```bash
python app.py
```

The API will be available at `http://localhost:8000`

## LLM Configuration

The agent supports multiple LLM providers. Configure one by setting environment variables:

### OpenAI (Default)
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-3.5-turbo
```

### Anthropic Claude
```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-key-here
export ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Groq
```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=your-key-here
export GROQ_MODEL=mixtral-8x7b-32768
```

**Supported Providers:**
- `openai` - GPT-3.5 Turbo, GPT-4, GPT-4 Turbo
- `anthropic` - Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku
- `groq` - Mixtral 8x7B, Llama 2 70B, Gemma 7B

See `.env.example` for all configuration options.

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

#### Query the Agent
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2 + 2?"}'
```

### API Documentation

Once running, visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## Deployment to Railway

### Prerequisites

- Railway account (https://railway.app)
- Git repository

### Steps

1. **Create a Git repository**:
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create a new project on Railway**:
   - Go to https://railway.app
   - Click "Create New Project"
   - Select "Deploy from GitHub" or "Create Empty Project"

3. **Connect your repository**:
   - If using GitHub, authorize Railway and select your repository
   - If using empty project, Railway will provide git instructions

4. **Push to Railway**:
```bash
git remote add railway <railway-git-url>
git push railway main
```

5. **Configure environment variables** (if needed):
   - Go to your Railway project settings
   - Add your LLM provider variables:
     - `LLM_PROVIDER` (e.g., `openai`, `anthropic`, `groq`)
     - `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`, `GROQ_API_KEY` depending on provider)
     - Optional: `OPENAI_MODEL`, `ANTHROPIC_MODEL`, `GROQ_MODEL` (defaults used if not set)

6. **Get your API URL**:
   - Railway will automatically assign a public URL
   - You'll see it in the Railway dashboard under "Deployments"
   - Format: `https://<project-name>.up.railway.app`

### Example API Calls on Railway

Replace `YOUR_RAILWAY_URL` with your actual Railway deployment URL:

```bash
# Health check
curl https://YOUR_RAILWAY_URL/health

# Query the agent
curl -X POST https://YOUR_RAILWAY_URL/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the current date?"}'
```

## Project Structure

```
.
├── app.py              # FastAPI application and agent setup
├── crewai.py           # Original agent definition (optional)
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration for Railway
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Troubleshooting

### Port binding error
The application uses the `$PORT` environment variable for Railway. Locally, it defaults to 8000.

### Agent not responding
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure CrewAI and its tools are properly configured
- Check Railway logs for error messages

### API returning 500 error
- Check the request format matches the schema (POST /ask with JSON body)
- Review Railway deployment logs
- Ensure all environment variables are set if required

## Next Steps

- Customize the agent's role, goal, and backstory in `app.py`
- Add more tools to expand agent capabilities
- Set up environment variables for sensitive data
- Add authentication/API keys if needed
