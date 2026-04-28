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

# Load config
if [[ -f railway.config ]]; then
    source railway.config
    echo -e "${DIM}Config: PROJECT_NAME=$PROJECT_NAME, SERVICE_NAME=$SERVICE_NAME${NC}"
else
    echo "Missing railway.config. Run from project root."
    exit 1
fi

# Load .env for secrets
if [[ -f .env ]]; then
    set -a
    source .env
    set +a
    echo -e "${DIM}Loaded .env${NC}"
fi

# Preflight
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Install: https://docs.railway.com/guides/cli"
    exit 1
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "OPENAI_API_KEY not set."
    exit 1
fi

echo ""
echo -e "${BOLD}Creating project '${PROJECT_NAME}'...${NC}"
echo ""
railway init -n "$PROJECT_NAME"

echo ""
echo -e "${BOLD}Provisioning PgVector database...${NC}"
echo ""
railway deploy -t "$DB_TEMPLATE_ID"

echo ""
echo -e "${DIM}Waiting ${DB_WAIT_TIME}s for database...${NC}"
sleep "$DB_WAIT_TIME"

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
    --variables "PORT=${PORT}"

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
