#!/bin/bash

############################################################################
#
#    Agno Railway Deployment
#
#    Usage: ./scripts/railway_up.sh
#
#    Prerequisites:
#      - Railway CLI installed
#      - Logged in via `railway login`
#      - OPENAI_API_KEY set in environment
#
############################################################################

set -e

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗  ██████╗ ███╗   ██╗ ██████╗
    ██╔══██╗██╔════╝ ████╗  ██║██╔═══██╗
    ███████║██║  ███╗██╔██╗ ██║██║   ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
BANNER
echo -e "${NC}"

# Load .env if it exists
if [[ -f .env ]]; then
    set -a
    source .env
    set +a
    echo -e "${DIM}Loaded .env${NC}"
fi

# Preflight
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Install: https://docs.railway.app/guides/cli"
    exit 1
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "OPENAI_API_KEY not set."
    exit 1
fi

echo -e "${BOLD}Initializing project...${NC}"
echo ""
railway init -n "agno"

echo ""
echo -e "${BOLD}Deploying PgVector database...${NC}"
echo ""
railway deploy -t 3jJFCA

echo ""
echo -e "${DIM}Waiting 10s for database...${NC}"
sleep 10

echo ""
echo -e "${BOLD}Creating application service...${NC}"
echo ""
railway add --service agent_os \
    --variables 'DB_USER=${{pgvector.PGUSER}}' \
    --variables 'DB_PASS=${{pgvector.PGPASSWORD}}' \
    --variables 'DB_HOST=${{pgvector.PGHOST}}' \
    --variables 'DB_PORT=${{pgvector.PGPORT}}' \
    --variables 'DB_DATABASE=${{pgvector.PGDATABASE}}' \
    --variables "DB_DRIVER=postgresql+psycopg" \
    --variables "WAIT_FOR_DB=True" \
    --variables "DATA_DIR=/data" \
    --variables "OPENAI_API_KEY=${OPENAI_API_KEY}" \
    --variables "PORT=8000"

# Add optional EXA_API_KEY if set
if [[ -n "$EXA_API_KEY" ]]; then
    echo -e "${DIM}Adding EXA_API_KEY...${NC}"
    railway variables --set "EXA_API_KEY=${EXA_API_KEY}" --service agent_os --skip-deploys
fi

# Add persistent volume for DuckDB data
echo ""
echo -e "${BOLD}Adding persistent volume...${NC}"
echo ""
railway volume add -m /data 2>/dev/null || echo -e "${DIM}Volume already exists or skipped${NC}"

# Wire bucket credentials if a bucket exists in the project
# NOTE: Create a bucket manually in the Railway dashboard first.
#       Name the bucket service "storage" so the variable references work.
echo ""
echo -e "${BOLD}Wiring storage bucket...${NC}"
echo -e "${DIM}If you have a bucket named 'storage' in this project, credentials will be linked.${NC}"
echo -e "${DIM}To create one: Railway Dashboard -> Create -> Bucket -> name it 'storage'${NC}"
echo ""
railway variables --set 'S3_ENDPOINT=${{storage.ENDPOINT}}' --service agent_os --skip-deploys 2>/dev/null || true
railway variables --set 'S3_BUCKET=${{storage.BUCKET}}' --service agent_os --skip-deploys 2>/dev/null || true
railway variables --set 'S3_ACCESS_KEY_ID=${{storage.ACCESS_KEY_ID}}' --service agent_os --skip-deploys 2>/dev/null || true
railway variables --set 'S3_SECRET_ACCESS_KEY=${{storage.SECRET_ACCESS_KEY}}' --service agent_os --skip-deploys 2>/dev/null || true
railway variables --set 'S3_REGION=${{storage.REGION}}' --service agent_os --skip-deploys 2>/dev/null || true

echo ""
echo -e "${BOLD}Deploying application...${NC}"
echo ""
railway up --service agent_os -d

echo ""
echo -e "${BOLD}Creating domain...${NC}"
echo ""
railway domain --service agent_os

echo ""
echo -e "${BOLD}Done.${NC} Domain may take ~5 minutes."
echo -e "${DIM}Logs: railway logs --service agent_os${NC}"
echo ""
