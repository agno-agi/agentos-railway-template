# Agent OS RailwayTemplate

Run agents, teams, and workflows as a production-ready API. 
Develop on Docker Desktop and deploy to Railway.

## Quickstart

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- [OpenAI API key](https://platform.openai.com/api-keys)

### Clone and configure

```sh
git clone https://github.com/agno-agi/agentos-railway.git agentos-railway
cd agentos-railway

cp example.env .env
# Add OPENAI_API_KEY to .env
```

> Agno works with any model provider. Update the agents in `/agents` and add dependencies to `pyproject.toml`.

### Start AgentOS

### Locally using Docker Compose

```sh
docker compose up -d --build
```

This starts:
- **AgentOS** (FastAPI server) on http://localhost:8000
- **PostgreSQL** with pgvector on localhost:5432

Open http://localhost:8000/docs to see the API.

### Connect to the control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" and select "Local"
3. Enter `http://localhost:8000`

### Stop AgentOS

```sh
docker compose down
```

### On Railway using the Railway CLI

1. Install the Railway CLI (More details [here](https://docs.railway.com/guides/cli)):

```sh
brew install railway
```

2. Login to your Railway account:

```sh
railway login
```

3. Run the deployment script:

```sh
./scripts/railway_up.sh
```

4. Monitor the deployment (Optional):

```sh
railway logs --service agent_os
```

5. Access the application via the Railway UI:

```sh
railway open
```

6. In the CLI, you will see the domain of your application. Click on it to access your AgentOS FastAPI server. You can navigate to `<railway-domain>/docs` to access the API documentation.

### Connect to the control plane

1. Open [os.agno.com](https://os.agno.com)
2. Click "Add OS" and select "Live"
3. Enter `<railway-domain>`

### Stopping your Railway Deployment

To stop your Railway deployment, you can run the following command:

```sh
railway down --service agent_os
railway down --service pgvector
```

This will stop your services on Railway.

Note: In order to start services again, in the same project on railway, you can run the `./scripts/railway_up.sh` script again but make sure to remove the railway init command as that will create a new project on Railway.


## Project Structure

```
agentos-docker/
├── agents/              # Your agents
├── app/                 # AgentOS entry point
├── db/                  # Database connection
├── scripts/             # Helper scripts
├── compose.yaml         # Docker Compose configuration
├── Dockerfile           # Container build
├── example.env          # Example environment variables
└── pyproject.toml       # Python dependencies
```

## Common Tasks

### Load a knowledge base

Locally:
```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

Railway:
```sh
railway ssh --service agent_os
python -m agents.knowledge_agent
```

### View logs
```sh
docker compose logs -f
```

### Restart after code changes
```sh
docker compose restart
```

### Updating your Railway Deployment

To update your Railway deployment, you can run the following command after making changes to the application:

```sh
railway up --service agent_os -d
```

This will trigger a new deployment of your application by creating a new docker image and deploying it to Railway.

### Railway Performance

Based on your requirements, please make sure to update the CPU and Memory limits in the `railway.json` file. We recommend using 2000 CPU and 4Gi Memory for the AgentOS and PgVector database.

### What the railway_up.sh script does:

The script does the following:

1. Initializes a new project on Railway
2. Deploys PgVector database on Railway
3. Creates the application service with environment variables already set (DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DATABASE, OPENAI_API_KEY)
4. Deploys the application
5. Creates a domain for your application

## Local Development

For development without Docker:

### Install uv
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup environment
```sh
./scripts/venv_setup.sh
source .venv/bin/activate
```

### Add dependencies

1. Edit `pyproject.toml`
2. Regenerate requirements:
```sh
./scripts/generate_requirements.sh
```
3. Rebuild:
```sh
docker compose up -d --build
```

## Learn More

- [Agno Documentation](https://docs.agno.com)
- [AgentOS Documentation](https://docs.agno.com/agent-os)
- [Discord Community](https://agno.link/discord)