# Agent OS Template

Welcome to Agent OS Railway Template: a robust, production-ready application for serving Agentic Applications as an API on Railway. It includes:

- An **AgentOS instance**: An API-based interface for production-ready Agentic Applications.
- A **PostgreSQL database** for storing Agent sessions, knowledge, and memories.

## Quickstart

Follow these steps to get your Agent OS up and running:

> [Get Docker Desktop](https://www.docker.com/products/docker-desktop) should be installed and running.
> [Get OpenAI API key](https://platform.openai.com/api-keys)

### Clone the repo

```sh
git clone https://github.com/agno-agi/agentos-railway-template.git
cd agentos-railway-template
```

### Configure API keys

We use GPT 5 Mini as the default model, please export the `OPENAI_API_KEY` environment variable to get started.

```sh
export OPENAI_API_KEY="YOUR_API_KEY_HERE"
```

> **Note**: You can use any model provider, just update the respective agents, teams and workflows and add the required library in the `pyproject.toml` and `requirements.txt` file.

## Running the application

The application can be run on two environments:

Locally using Docker Compose or on Railway using the Railway CLI.

### Locally using Docker Compose

Run the application using docker compose (Remove the `--build` flag if you already have the image built):

```sh
docker compose up -d --build
```

This command starts:

- The **AgentOS instance**, which is a FastAPI server, running on [http://localhost:8080](http://localhost:8080).
- The **PostgreSQL database**, accessible on `localhost:5432`.

Once started, you can:

- Test the API at [http://localhost:8080/docs](http://localhost:8080/docs).

### Connect to AgentOS UI

- Open the [Agno AgentOS UI](https://os.agno.com).
- Connect your OS with `http://localhost:8080` as the endpoint. You can name it `AgentOS` (or any name you prefer).
- Explore all the features of AgentOS or go straight to the Chat page to interact with your Agents, Teams and Workflows.

### How to load the knowledge base locally

To load the knowledge base, you can use the following command:

```sh
docker exec -it agentos-api python -m agents.knowledge_agent
```

### Stop the application

When you're done, stop the application using:

```sh
docker compose down
```

## Railway Deployment

To deploy the application on Railway, please follow the steps below:

1. Install the Railway CLI (More details [here](https://docs.railway.com/guides/cli)):

```sh
brew install railway
```

2. Login to your Railway account:

```sh
railway login
```

Note: Remember to either export the `OPENAI_API_KEY` environment variable.

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

7. On Agno AgentOS UI, connect your OS with the domain you just created.

- Open the [Agno AgentOS UI](https://os.agno.com).
- Connect your OS with `<railway-domain>` as the endpoint.

Congratulations! You have successfully deployed Agent OS on Railway. Your OS is now live and ready to use. You can now start using your Agents, Teams and Workflows as well as take a look at your Sessions, Memories, Knowledge and Metrics.

### Updating your Railway Deployment

To update your Railway deployment, you can run the following command after making changes to the application:

```sh
railway up --service agent_os -d
```

This will trigger a new deployment of your application by creating a new docker image and deploying it to Railway.

### Adding Knowledge on Railway

To add knowledge to the Agno Knowledge Agent, run the following command:

```sh
railway ssh --service agent_os
```

This command will open a ssh session to the AgentOS service.

Once you are in the ssh session, you can run the following command to add knowledge to the Knowledge Agent:

```sh
python -m agents.knowledge_agent
```

### Stopping your Railway Deployment

To stop your Railway deployment, you can run the following command:

```sh
railway down --service agent_os
railway down --service pgvector
```

This will stop your services on Railway.

Note: In order to start services again, in the same project on railway, you can run the `./scripts/railway_up.sh` script again but make sure to remove the railway init command as that will create a new project on Railway.

### Railway Performance

Based on your requirements, please make sure to update the CPU and Memory limits in the `railway.json` file. We recommend using 2000 CPU and 4Gi Memory for the AgentOS and PgVector database.

### What the railway_up.sh script does:

The script does the following:

1. Initializes a new project on Railway
2. Deploys PgVector database on Railway
3. Creates the application service with environment variables already set (DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DATABASE, OPENAI_API_KEY)
4. Deploys the application
5. Creates a domain for your application

## Development Setup

To setup your local virtual environment:

### Install `uv`

We use `uv` for python environment and package management. Install it by following the the [`uv` documentation](https://docs.astral.sh/uv/#getting-started) or use the command below for unix-like systems:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Create Virtual Environment & Install Dependencies

Run the `dev_setup.sh` script. This will create a virtual environment and install project dependencies:

```sh
./scripts/dev_setup.sh
```

### Activate Virtual Environment

Activate the created virtual environment:

```sh
source .venv/bin/activate
```

(On Windows, the command might differ, e.g., `.venv\Scripts\activate`)

## Managing Python Dependencies

If you need to add or update python dependencies:

### Modify pyproject.toml

Add or update your desired Python package dependencies in the `[dependencies]` section of the `pyproject.toml` file.

### Generate requirements.txt

The `requirements.txt` file is used to build the application image. After modifying `pyproject.toml`, regenerate `requirements.txt` using:

```sh
./scripts/generate_requirements.sh
```

To upgrade all existing dependencies to their latest compatible versions, run:

```sh
./scripts/generate_requirements.sh upgrade
```

### Rebuild Docker Images

Rebuild your Docker images to include the updated dependencies:

```sh
docker compose up -d --build
```
