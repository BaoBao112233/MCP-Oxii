#!/bin/bash

# MCP-Oxii Temp API Docker Runner Script
# Provides easy commands to manage the Planner API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Functions
print_usage() {
    echo -e "${BLUE}MCP-Oxii Temp API Docker Management${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start                 Start the API service"
    echo "  start-with-cache      Start API with Redis cache"
    echo "  start-with-db         Start API with PostgreSQL database"
    echo "  start-full            Start API with all services"
    echo "  stop                  Stop all services"
    echo "  restart               Restart the API service"
    echo "  logs                  Show logs (add -f to follow)"
    echo "  status                Show service status"
    echo "  build                 Build the Docker image"
    echo "  shell                 Open shell in API container"
    echo "  test                  Run API tests"
    echo "  clean                 Clean up containers and volumes"
    echo "  help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start              # Start basic API"
    echo "  $0 start-full         # Start with all services"
    echo "  $0 logs -f            # Follow logs in real-time"
    echo "  $0 test               # Run API tests"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
}

create_env_if_missing() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file from .env.example${NC}"
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please review and adjust settings if needed.${NC}"
    fi
}

create_directories() {
    echo -e "${BLUE}Creating necessary directories...${NC}"
    mkdir -p data logs
}

# Commands
cmd_start() {
    echo -e "${GREEN}Starting Planner API...${NC}"
    create_env_if_missing
    create_directories
    docker compose up -d planner-api
    echo -e "${GREEN}API started! Available at: http://localhost:8000${NC}"
}

cmd_start_with_cache() {
    echo -e "${GREEN}Starting Planner API with Redis cache...${NC}"
    create_env_if_missing
    create_directories
    docker compose --profile with-cache up -d
    echo -e "${GREEN}API with cache started! Available at: http://localhost:8000${NC}"
}

cmd_start_with_db() {
    echo -e "${GREEN}Starting Planner API with PostgreSQL database...${NC}"
    create_env_if_missing
    create_directories
    docker compose --profile with-db up -d
    echo -e "${GREEN}API with database started! Available at: http://localhost:8000${NC}"
}

cmd_start_full() {
    echo -e "${GREEN}Starting Planner API with all services...${NC}"
    create_env_if_missing
    create_directories
    docker compose --profile with-cache --profile with-db up -d
    echo -e "${GREEN}Full stack started! Available at: http://localhost:8000${NC}"
}

cmd_stop() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    docker compose --profile with-cache --profile with-db down
    echo -e "${GREEN}All services stopped.${NC}"
}

cmd_restart() {
    echo -e "${YELLOW}Restarting Planner API...${NC}"
    docker compose restart planner-api
    echo -e "${GREEN}API restarted!${NC}"
}

cmd_logs() {
    if [ "$1" = "-f" ]; then
        docker compose logs -f planner-api
    else
        docker compose logs planner-api
    fi
}

cmd_status() {
    echo -e "${BLUE}Service Status:${NC}"
    docker compose ps
    echo ""
    echo -e "${BLUE}Health Check:${NC}"
    curl -s http://localhost:8000/health || echo -e "${RED}API not responding${NC}"
}

cmd_build() {
    echo -e "${BLUE}Building Docker image...${NC}"
    docker compose build planner-api
    echo -e "${GREEN}Build completed!${NC}"
}

cmd_shell() {
    echo -e "${BLUE}Opening shell in API container...${NC}"
    docker compose exec planner-api /bin/bash
}

cmd_test() {
    echo -e "${BLUE}Running API tests...${NC}"
    if [ -f test_api.py ]; then
        docker compose exec planner-api python test_api.py
    else
        echo -e "${YELLOW}No test file found. Running basic health check...${NC}"
        curl -s http://localhost:8000/health
    fi
}

cmd_clean() {
    echo -e "${YELLOW}Cleaning up containers and volumes...${NC}"
    read -p "This will remove all containers and volumes. Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose --profile with-cache --profile with-db down -v
        docker system prune -f
        echo -e "${GREEN}Cleanup completed!${NC}"
    else
        echo -e "${BLUE}Cleanup cancelled.${NC}"
    fi
}

# Main script
check_docker

case "${1:-help}" in
    start)
        cmd_start
        ;;
    start-with-cache)
        cmd_start_with_cache
        ;;
    start-with-db)
        cmd_start_with_db
        ;;
    start-full)
        cmd_start_full
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    logs)
        cmd_logs "$2"
        ;;
    status)
        cmd_status
        ;;
    build)
        cmd_build
        ;;
    shell)
        cmd_shell
        ;;
    test)
        cmd_test
        ;;
    clean)
        cmd_clean
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac