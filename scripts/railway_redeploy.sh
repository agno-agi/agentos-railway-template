#!/bin/bash

############################################################################
#
#    Agno Railway Redeploy
#
#    Usage: ./scripts/railway_redeploy.sh
#
#    Redeploys the app service to an existing Railway project.
#    Run ./scripts/railway_up.sh first for initial provisioning.
#
############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

# Load config
if [[ -f "$ROOT_DIR/railway.config" ]]; then
    source "$ROOT_DIR/railway.config"
    echo -e "${DIM}Config: SERVICE_NAME=$SERVICE_NAME${NC}"
else
    echo "Missing railway.config"
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
