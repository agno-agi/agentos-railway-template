#!/bin/bash

############################################################################
#
#    Agno Railway Deployment
#
#    Usage: ./scripts/railway_up.sh [OPTIONS]
#
#    Prerequisites:
#      - Railway CLI installed
#      - Logged in via `railway login`
#      - OPENAI_API_KEY set in environment (fresh deploy only)
#
############################################################################

set -e

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

PROJECT=""
ENVIRONMENT="production"
APP_SERVICE="agent-os"
UPDATE=false

usage() {
    cat <<EOF
Usage: ./scripts/railway_up.sh [OPTIONS]

Options:
  -U, --update                  Update the currently linked project (re-deploy only)
  -p, --project PROJECT         Deploy to an existing Railway project (ID recommended)
  -e, --environment ENVIRONMENT Railway environment for project linking (default: production)
  -s, --service SERVICE         Railway service name to deploy (default: agent-os)
  -h, --help                    Show this help message
EOF
}

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

while [[ $# -gt 0 ]]; do
    case "$1" in
        -U|--update)
            UPDATE=true
            shift
            ;;
        -p|--project)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Missing value for $1."
                usage
                exit 1
            fi
            PROJECT="$2"
            shift 2
            ;;
        -e|--environment)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Missing value for $1."
                usage
                exit 1
            fi
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--service)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Missing value for $1."
                usage
                exit 1
            fi
            APP_SERVICE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ "$UPDATE" == true ]]; then
    echo ""
    echo -e "${BOLD}Updating currently linked project...${NC}"
    echo ""
    railway up --service "$APP_SERVICE" -d

    echo ""
    echo -e "${BOLD}Done.${NC} Update deployed."
    echo -e "${DIM}Logs: railway logs --service ${APP_SERVICE}${NC}"
    echo ""
    exit 0
fi

if [[ -n "$PROJECT" ]]; then
    echo ""
    echo -e "${BOLD}Linking to existing Railway project...${NC}"
    echo ""
    railway link --project "$PROJECT" --environment "$ENVIRONMENT"

    echo ""
    echo -e "${BOLD}Deploying application...${NC}"
    echo ""
    railway up --service "$APP_SERVICE" -d

    echo ""
    echo -e "${BOLD}Done.${NC} Deployed to existing project."
    echo -e "${DIM}Logs: railway logs --service ${APP_SERVICE}${NC}"
    echo ""
    exit 0
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
railway add --service "$APP_SERVICE" \
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
echo -e "${BOLD}Deploying application...${NC}"
echo ""
railway up --service "$APP_SERVICE" -d

echo ""
echo -e "${BOLD}Creating domain...${NC}"
echo ""
railway domain --service "$APP_SERVICE"

echo ""
echo -e "${BOLD}Done.${NC} Domain may take ~5 minutes."
echo -e "${DIM}Logs: railway logs --service ${APP_SERVICE}${NC}"
echo ""
