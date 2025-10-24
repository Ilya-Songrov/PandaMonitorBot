#!/bin/bash

# PandaMonitorBot - Development Utilities Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "🐼 PandaMonitorBot - Development Utilities"
    echo "========================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start the bot"
    echo "  stop            Stop the bot"
    echo "  restart         Restart the bot"
    echo "  logs            Show bot logs"
    echo "  status          Show container status"
    echo "  shell           Enter bot container shell"
    echo "  build           Build Docker image"
    echo "  clean           Clean Docker images and containers"
    echo "  setup           Initial setup (create .env from example)"
    echo "  test            Run tests (if any)"
    echo "  help            Show this help message"
    echo ""
}

case "$1" in
    start)
        print_status "Starting PandaMonitorBot..."
        docker compose up -d
        print_success "Bot started!"
        ;;
    stop)
        print_status "Stopping PandaMonitorBot..."
        docker compose down
        print_success "Bot stopped!"
        ;;
    restart)
        print_status "Restarting PandaMonitorBot..."
        docker compose restart
        print_success "Bot restarted!"
        ;;
    logs)
        print_status "Showing bot logs (Ctrl+C to exit)..."
        docker compose logs -f
        ;;
    status)
        print_status "Container status:"
        docker compose ps
        ;;
    shell)
        print_status "Entering bot container shell..."
        docker compose exec panda_monitor_bot bash
        ;;
    build)
        print_status "Building Docker image..."
        docker compose build --no-cache
        print_success "Image built successfully!"
        ;;
    clean)
        print_warning "This will remove all unused Docker images and containers!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker compose down
            docker system prune -f
            print_success "Docker cleanup completed!"
        else
            print_status "Cleanup cancelled."
        fi
        ;;
    setup)
        if [ -f ".env" ]; then
            print_warning ".env file already exists!"
        else
            print_status "Creating .env file from .env.example..."
            cp .env.example .env
            print_success ".env file created!"
            print_warning "Please edit .env file with your bot token and user IDs"
        fi
        ;;
    test)
        print_status "Running tests..."
        # Add test commands here when tests are implemented
        print_warning "No tests configured yet"
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac