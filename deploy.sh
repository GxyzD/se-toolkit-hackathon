#!/bin/bash

# Study Group Matcher - Deployment Script
# This script handles both local development and VM production deployment

set -e

echo "🚀 Study Group Matcher - Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"
echo ""

# Ask for deployment mode
echo "Select deployment mode:"
echo "1) Local Development (SQLite, hot reload)"
echo "2) Production (PostgreSQL, VM deployment)"
read -p "Enter choice (1 or 2) [default: 1]: " MODE
MODE=${MODE:-1}

if [ "$MODE" = "1" ]; then
    echo ""
    echo -e "${YELLOW}🔧 Starting local development environment...${NC}"
    
    # Update .env for local development
    if [ -f .env ]; then
        echo "DATABASE_URL=sqlite:///./students.db" > .env.local
        grep -v "DATABASE_URL" .env >> .env.local || true
        mv .env.local .env
        echo -e "${GREEN}✅ Updated .env for SQLite${NC}"
    fi
    
    # Build and start
    echo ""
    echo "📦 Building Docker images..."
    docker-compose build
    
    echo ""
    echo "🚀 Starting services..."
    docker-compose up -d
    
    echo ""
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    # Seed database
    echo ""
    echo "🌱 Seeding database with sample data..."
    docker-compose exec backend python -m app.seed || echo -e "${YELLOW}⚠️  Database seeding skipped (may already be seeded)${NC}"
    
    echo ""
    echo -e "${GREEN}✅ Local development environment started!${NC}"
    echo ""
    echo "📍 Frontend: http://localhost:80"
    echo "🔌 Backend API: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    
elif [ "$MODE" = "2" ]; then
    echo ""
    echo -e "${YELLOW}🌐 Starting production deployment...${NC}"
    
    # Check if .env is configured
    if grep -q "your_telegram_bot_token" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Telegram bot token not configured${NC}"
    fi
    
    # Update .env for production
    echo ""
    echo "Updating .env for production..."
    if [ -f .env ]; then
        sed -i 's|DATABASE_URL=sqlite:///./students.db|DATABASE_URL=postgresql://postgres:postgres@db:5432/study_matcher|g' .env 2>/dev/null || \
        sed -i '' 's|DATABASE_URL=sqlite:///./students.db|DATABASE_URL=postgresql://postgres:postgres@db:5432/study_matcher|g' .env 2>/dev/null || true
        echo -e "${GREEN}✅ Updated .env for PostgreSQL${NC}"
    fi
    
    # Build and start in production mode
    echo ""
    echo "📦 Building Docker images..."
    docker-compose build --no-cache
    
    echo ""
    echo "🚀 Starting services in detached mode..."
    docker-compose up -d
    
    echo ""
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Seed database
    echo ""
    echo "🌱 Seeding database with sample data..."
    docker-compose exec backend python -m app.seed || echo -e "${YELLOW}⚠️  Database seeding skipped${NC}"
    
    # Setup Telegram webhook if configured
    if grep -q "BOT_TOKEN=" .env && ! grep -q "your_telegram_bot_token" .env; then
        echo ""
        echo "📱 Setting up Telegram webhook..."
        read -p "Enter your domain/VM IP (e.g., https://your-domain.com): " DOMAIN
        curl -X POST "http://localhost:8000/api/telegram/setup-webhook?webhook_url=${DOMAIN}/api/telegram/webhook" || \
        echo -e "${YELLOW}⚠️  Telegram webhook setup failed${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Production deployment completed!${NC}"
    echo ""
    echo "📍 Frontend: http://your-domain-or-ip:80"
    echo "🔌 Backend API: http://your-domain-or-ip:8000"
    echo "📖 API Docs: http://your-domain-or-ip:8000/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    echo "Restart services: docker-compose restart"
    
else
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Open the website and register"
echo "2. View your matches and send requests"
echo "3. (Optional) Configure Telegram bot for notifications"
echo "4. Use /help on Telegram bot for commands"
echo "=========================================="
