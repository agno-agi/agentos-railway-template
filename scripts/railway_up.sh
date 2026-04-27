#!/bin/bash

############################################################################
#
#    Agno Railway Deployment
#
#    Usage:
#      ./scripts/railway_up.sh           # Fresh deploy (provisions everything)
#      ./scripts/railway_up.sh update    # Re-deploy code only
#      ./scripts/railway_up.sh link ID   # Link to existing project, then deploy
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
    echo "Missing railway.config. Copy from railway.config.example and edit."
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

# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

cmd_update() {
    echo ""
    echo -e "${BOLD}Re-deploying ${SERVICE_NAME}...${NC}"
    echo ""
    railway up --service "$SERVICE_NAME" -d

    echo ""
    echo -e "${BOLD}Done.${NC}"
    echo -e "${DIM}Logs: railway logs --service ${SERVICE_NAME}${NC}"
}

cmd_link() {
    local project_id="$1"
    if [[ -z "$project_id" ]]; then
        echo "Usage: ./scripts/railway_up.sh link <project-id>"
        exit 1
    fi

    echo ""
    echo -e "${BOLD}Linking to project ${project_id}...${NC}"
    echo ""
    railway link --project "$project_id" --environment "$RAILWAY_ENVIRONMENT"

    echo ""
    echo -e "${BOLD}Deploying ${SERVICE_NAME}...${NC}"
    echo ""
    railway up --service "$SERVICE_NAME" -d

    echo ""
    echo -e "${BOLD}Done.${NC}"
    echo -e "${DIM}Logs: railway logs --service ${SERVICE_NAME}${NC}"
}

cmd_fresh() {
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
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

case "${1:-}" in
    update)
        cmd_update
        ;;
    link)
        cmd_link "$2"
        ;;
    ""|fresh)
        cmd_fresh
        ;;
    *)
        echo "Usage: ./scripts/railway_up.sh [update|link <project-id>]"
        exit 1
        ;;
esac
