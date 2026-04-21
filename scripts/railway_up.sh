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
railway init -n "agent-os"

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
railway add --service agent-os \
    --variables 'DB_USER=${{pgvector.PGUSER}}' \
    --variables 'DB_PASS=${{pgvector.PGPASSWORD}}' \
    --variables 'DB_HOST=${{pgvector.PGHOST}}' \
    --variables 'DB_PORT=${{pgvector.PGPORT}}' \
    --variables 'DB_DATABASE=${{pgvector.PGDATABASE}}' \
    --variables "DB_DRIVER=postgresql+psycopg" \
    --variables "WAIT_FOR_DB=True" \
    --variables "OPENAI_API_KEY=${OPENAI_API_KEY}" \
    --variables "WHATSAPP_ENABLED=${WHATSAPP_ENABLED:-false}" \
    --variables "WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN}" \
    --variables "WHATSAPP_PHONE_NUMBER_ID=${WHATSAPP_PHONE_NUMBER_ID}" \
    --variables "WHATSAPP_VERIFY_TOKEN=${WHATSAPP_VERIFY_TOKEN}" \
    --variables "WHATSAPP_APP_SECRET=${WHATSAPP_APP_SECRET}" \
    --variables "PORT=8000"

echo ""
echo -e "${BOLD}Deploying application...${NC}"
echo ""
railway up --service agent-os -d

echo ""
echo -e "${BOLD}Creating domain...${NC}"
echo ""
railway domain --service agent-os

echo ""
echo -e "${BOLD}Done.${NC} Domain may take ~5 minutes."
echo -e "${DIM}Logs: railway logs --service agent-os${NC}"
echo ""
