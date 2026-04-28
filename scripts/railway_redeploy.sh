#!/bin/bash

############################################################################
#
#    Agno Railway Redeploy
#
#    Usage: ./scripts/railway_redeploy.sh
#
#    Prerequisites:
#      - Railway CLI installed
#      - Logged in via `railway login`
#      - Project already deployed via ./scripts/railway_up.sh
#
############################################################################

set -e

# Colors
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

# Load config
if [[ -f railway.config ]]; then
    source railway.config
    echo -e "${DIM}Config: SERVICE_NAME=$SERVICE_NAME${NC}"
else
    echo "Missing railway.config. Run from project root."
    exit 1
fi

# Preflight
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Install: https://docs.railway.com/guides/cli"
    exit 1
fi

if ! railway status &> /dev/null; then
    echo "Not linked to a Railway project. Run ./scripts/railway_up.sh first."
    exit 1
fi

echo ""
echo -e "${BOLD}Redeploying ${SERVICE_NAME}...${NC}"
echo ""
railway up --service "$SERVICE_NAME" -d

echo ""
echo -e "${BOLD}Done.${NC}"
echo -e "${DIM}Logs: railway logs --service ${SERVICE_NAME}${NC}"
echo ""
