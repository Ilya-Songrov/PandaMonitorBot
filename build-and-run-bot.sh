#!/bin/bash

# PandaMonitorBot - Build and Run Script
# This script builds and runs the Telegram bot using Docker

set -e

echo "🐼 PandaMonitorBot - Build and Run Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    print_status "Creating .env file from .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file with your bot token and user IDs before running again!"
        print_status "You can get bot token from @BotFather on Telegram"
        print_status "You can get your user ID from @userinfobot on Telegram"
        exit 1
    else
        print_error ".env.example file not found!"
        exit 1
    fi
fi

# Check if required environment variables are set
source .env
if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" = "your_bot_token_here" ]; then
    print_error "BOT_TOKEN is not set in .env file!"
    print_status "Please edit .env file with your bot token from @BotFather"
    exit 1
fi

if [ -z "$ALLOWED_USER_IDS" ] || [ "$ALLOWED_USER_IDS" = "123456789,987654321" ]; then
    print_error "ALLOWED_USER_IDS is not set in .env file!"
    print_status "Please edit .env file with your user IDs (get from @userinfobot)"
    exit 1
fi

# Create logs directory if it doesn't exist
print_status "Setting up directories..."
if [ -n "$DEPLOY_ROOT_DIR" ] && [ "$DEPLOY_ROOT_DIR" != "." ]; then
    # Using DEPLOY_ROOT_DIR from .env
    LOGS_DIR="${DEPLOY_ROOT_DIR}/logs"
    DATA_DIR="${DEPLOY_ROOT_DIR}/data"
    
    mkdir -p "$LOGS_DIR"
    chmod 777 "$LOGS_DIR"
    
    mkdir -p "$DATA_DIR"
    chmod 755 "$DATA_DIR"
    
    # Copy .env to data directory if it doesn't exist
    if [ ! -f "$DATA_DIR/.env" ]; then
        print_status "Copying .env to $DATA_DIR"
        cp .env "$DATA_DIR/.env"
        chmod 644 "$DATA_DIR/.env"
    fi
    
    print_status "Logs directory: $LOGS_DIR"
    print_status "Data directory: $DATA_DIR"
else
    # Using local directories
    mkdir -p logs
    chmod 777 logs
    
    mkdir -p data
    chmod 755 data
    
    # Copy .env to data directory if it doesn't exist
    if [ ! -f "data/.env" ]; then
        print_status "Copying .env to data/"
        cp .env data/.env
        chmod 644 "data/.env"
    fi
    
    print_status "Logs directory: ./logs"
    print_status "Data directory: ./data"
fi

print_status "Stopping existing containers..."
docker compose down 2>/dev/null || true

print_status "Building Docker image..."
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
if [[ "$UBUNTU_VERSION" == "24.04" ]]; then
    print_warning "Detected Ubuntu 24.04 — using cache-bypass workaround (no native --no-cache support)"
    docker compose build --build-arg NO_CACHE=$(date +%s)
else
    docker compose build --no-cache
fi

print_success "Docker image built successfully!"

print_status "Starting the bot..."
docker compose up -d

# Wait a bit for the container to start
sleep 3

# Check if container is running
if docker compose ps | grep -q "Up"; then
    print_success "🐼 PandaMonitorBot is now running!"
    print_status "Container name: panda-monitor-bot"
    print_status "Logs directory: ./logs"
    echo ""
    print_status "Useful commands:"
    echo "  View logs:           docker compose logs -f"
    echo "  Stop bot:            docker compose down"
    echo "  Restart bot:         docker compose restart"
    echo "  Rebuild and restart: ./build-and-run-bot.sh"
    echo ""
    print_status "Checking bot status..."
    docker compose logs --tail=10
else
    print_error "Failed to start the bot!"
    print_status "Checking logs for errors..."
    docker compose logs --tail=20
    exit 1
fi