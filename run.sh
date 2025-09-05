#!/bin/bash

# Define color and formatting codes
BOLD='\033[1m'
GREEN='\033[1;32m'
WHITE='\033[1;37m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
# Unicode character for tick mark
TICK='\u2713'

# Default port
DEFAULT_PORT=8901
webui_port=$DEFAULT_PORT

# Read PORT from .env if exists
ENV_FILE=".env"
if [[ -f "$ENV_FILE" ]]; then
    port_value=$(grep -E '^PORT=' "$ENV_FILE" | cut -d'=' -f2)
    if [[ -n "$port_value" ]]; then
        webui_port=$port_value
    fi
fi

# Usage information
usage() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --up              Start and recreate the compose project docker compose up). Default."
    echo "  --down            Terminate and remove the compose project (docker compose down)."
    echo "  --stop            Stop running containers (docker compose stop)."
    echo "  --start           Start existing stopped containers (docker compose start)."
    echo "  --logs            Show logs of the compose project (docker compose logs -f)."
    echo "  -q, --quiet       Run script in headless mode."
    echo "  -h, --help        Show this help message."
    echo ""
    echo "Examples:"
    echo "  $0 --up"
    echo "  $0 --stop"
    echo "  $0 --logs"
    echo ""
}

# Default values
headless=false
action="--up"  # 默认动作

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --up|--down|--stop|--start|--logs)
            action="$key"
            ;;
        -q|--quiet)
            headless=true
            ;;
        -h|--help)
            usage
            exit
            ;;
        *)
            # Unknown option
            echo "Unknown option: $key"
            usage
            exit 1
            ;;
    esac
    shift # past argument or value
done

COMPOSE_CMD="docker compose -f docker-compose.yaml"

confirm_action() {
    local msg="$1"
    local choice=""

    if [[ $headless == true ]]; then
        echo -ne "${WHITE}${BOLD}Running in headless mode... ${NC}"
        choice="Y"
    else
        echo -ne "${WHITE}${BOLD}${msg} (Y/n): ${NC}"
        read -n1 -s choice
        echo
    fi

    if [[ $choice == "" || $choice == "Y" ]]; then
        return 0
    else
        echo "Aborted."
        exit 0
    fi
}

# Execute action
case $action in
    --up)
        # Recap of environment variables
        echo
        echo -e "${WHITE}${BOLD}Current Setup:${NC}"
        echo -e "   ${GREEN}${BOLD}WebUI Port:${NC} $webui_port"
        echo

        confirm_action "Do you want to run 'docker compose up'?"
        COMPOSE_CMD+=" up -d --remove-orphans --force-recreate"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}${BOLD}Compose project is up.${NC}"
        else
            echo -e "${RED}${BOLD}Failed to bring up the compose project.${NC}"
        fi
        ;;
    --down)
        confirm_action "Do you want to run 'docker compose down'?"
        COMPOSE_CMD+=" down --remove-orphans"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}${BOLD}Compose project terminated.${NC}"
        else
            echo -e "${RED}${BOLD}Failed to terminate the compose project.${NC}"
        fi
        ;;
    --stop)
        confirm_action "Do you want to run 'docker compose stop'?"
        COMPOSE_CMD+=" stop"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}${BOLD}Compose project stopped.${NC}"
        else
            echo -e "${RED}${BOLD}Failed to stop the compose project.${NC}"
        fi
        ;;
    --start)
        confirm_action "Do you want to run 'docker compose start'?"
        COMPOSE_CMD+=" start"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}${BOLD}Compose project started.${NC}"
        else
            echo -e "${RED}${BOLD}Failed to start the compose project.${NC}"
        fi
        ;;
    --logs)
        COMPOSE_CMD+=" logs --tail 100 -f"
        ;;
    *)
        echo -e "${RED}Unknown action: $action${NC}"
        exit 1
        ;;
esac


# Execute the command with the current user
eval "$COMPOSE_CMD" &

# Capture the background process PID
PID=$!

# Wait for the command to finish
wait $PID

echo
# Check exit status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}${BOLD}Compose project execed successfully.${NC}"
else
    echo -e "${RED}${BOLD}There was an error starting the compose project.${NC}"
fi