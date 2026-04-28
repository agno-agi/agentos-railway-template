#!/bin/bash

############################################################################
#
#    Agno Railway Setup (first-time provisioning)
#
#    Usage: ./scripts/railway_up.sh
#    Redeploy: ./scripts/railway_redeploy.sh
#
#    Configuration: Edit railway.config before running
#
############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

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

# Load config
if [[ -f "$ROOT_DIR/railway.config" ]]; then
    source "$ROOT_DIR/railway.config"
    echo -e "${DIM}Config: PROJECT_NAME=$PROJECT_NAME, SERVICE_NAME=$SERVICE_NAME${NC}"
else
    echo "Missing railway.config"
    exit 1
fi

# Load .env for secrets
if [[ -f "$ROOT_DIR/.env" ]]; then
    set -a
    source "$ROOT_DIR/.env"
    set +a
fi

# Preflight
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Install: https://docs.railway.com/guides/cli"
    exit 1
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "OPENAI_API_KEY not set. Add it to .env"
    exit 1
fi

echo ""
echo -e "${BOLD}Creating project '${PROJECT_NAME}'...${NC}"
echo ""
railway init -n "$PROJECT_NAME"

echo ""
echo -e "${BOLD}Provisioning PgVector database...${NC}"
echo ""
railway deploy -t 3jJFCA

echo -e "${DIM}Waiting 10s for database...${NC}"
sleep 10

echo ""
echo -e "${BOLD}Creating service '${SERVICE_NAME}'...${NC}"
echo ""
railway add --service "$SERVICE_NAME" \
    --variables 'DB_USER=${{pgvector.PGUSER}}' \
    --variables 'DB_PASS=${{pgvector.PGPASSWORD}}' \
    --variables 'DB_HOST=${{pgvector.PGHOST}}' \
    --variables 'DB_PORT=${{pgvector.PGPORT}}' \
    --variables 'DB_DATABASE=${{pgvector.PGDATABASE}}' \
    --variables "DB_DRIVER=postgresql+psycopg" \
    --variables "WAIT_FOR_DB=True" \
    --variables "OPENAI_API_KEY=${OPENAI_API_KEY}" \
    --variables "PORT=8000"

echo ""
echo -e "${BOLD}Deploying ${SERVICE_NAME}...${NC}"
echo ""
railway up --service "$SERVICE_NAME" -d

echo ""
echo -e "${BOLD}Creating domain...${NC}"
echo ""
railway domain --service "$SERVICE_NAME"

echo ""
echo -e "${BOLD}Done.${NC} Domain may take ~5 minutes."
echo -e "${DIM}Logs: railway logs --service ${SERVICE_NAME}${NC}"
echo ""
