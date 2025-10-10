#!/bin/bash

# 🚀 Quick Deployment Script for PKP Material Dashboard
# Run this on your VPS after initial setup

set -e  # Exit on error

echo "🚀 PKP Material Dashboard - Quick Deployment"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Please don't run as root. Use your pkp user account.${NC}"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Prompt for deployment type
echo "Select deployment type:"
echo "1) Development (SQLite, local testing)"
echo "2) Production (PostgreSQL, recommended for VPS)"
read -p "Enter choice [1-2]: " DEPLOY_TYPE

if [ "$DEPLOY_TYPE" = "1" ]; then
    COMPOSE_FILE="docker-compose.yml"
    ENV_FILE=".env"
    echo -e "${YELLOW}📦 Development deployment selected${NC}"
elif [ "$DEPLOY_TYPE" = "2" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_FILE=".env.production"
    echo -e "${GREEN}🏭 Production deployment selected${NC}"
else
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi

echo ""

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  Environment file $ENV_FILE not found${NC}"
    
    if [ -f ".env.docker" ]; then
        echo "Creating $ENV_FILE from template..."
        cp .env.docker "$ENV_FILE"
        echo -e "${YELLOW}📝 Please edit $ENV_FILE and add your configuration${NC}"
        echo ""
        read -p "Press Enter after you've configured $ENV_FILE..." 
    else
        echo -e "${RED}❌ Template file .env.docker not found${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment file found${NC}"
echo ""

# Generate secure secrets if needed
echo "🔐 Checking for secure secrets..."

if grep -q "your-super-secret-key" "$ENV_FILE"; then
    echo "Generating Flask secret key..."
    FLASK_SECRET=$(openssl rand -hex 32)
    sed -i "s/your-super-secret-key-change-this-in-production-use-random-64-chars/$FLASK_SECRET/" "$ENV_FILE"
    echo -e "${GREEN}✅ Flask secret key generated${NC}"
fi

if grep -q "change-this-strong-password" "$ENV_FILE"; then
    echo "⚠️  Please set a strong PostgreSQL password in $ENV_FILE"
fi

if grep -q "change-this-n8n-password" "$ENV_FILE"; then
    echo "⚠️  Please set a strong n8n password in $ENV_FILE"
fi

echo ""

# Pull latest images
echo "📥 Pulling Docker images..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

echo ""

# Build custom images
echo "🔨 Building application images..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build

echo ""

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true

echo ""

# Start services
echo "🚀 Starting services..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check container status
echo ""
echo "📊 Container Status:"
docker compose -f "$COMPOSE_FILE" ps

echo ""

# Run database migrations for production
if [ "$DEPLOY_TYPE" = "2" ]; then
    echo "🗄️  Creating database tables..."
    docker compose -f "$COMPOSE_FILE" exec -T dashboard python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database tables created!')
" 2>/dev/null || echo "⚠️  Database might already be initialized"
fi

echo ""

# Show logs
echo "📋 Recent logs:"
docker compose -f "$COMPOSE_FILE" logs --tail=20

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo "=============================================="
echo ""

# Show access information
if [ "$DEPLOY_TYPE" = "1" ]; then
    echo "🌐 Access your dashboard at:"
    echo "   Dashboard: http://localhost:5001"
    echo "   n8n:       http://localhost:5678"
else
    echo "🌐 Configure your domain DNS and access at:"
    echo "   Dashboard: https://dashboard.yourdomain.com"
    echo "   n8n:       https://n8n.yourdomain.com"
    echo ""
    echo "🔒 Don't forget to obtain SSL certificates:"
    echo "   Run: ./setup-ssl.sh"
fi

echo ""
echo "📊 Useful commands:"
echo "   View logs:    docker compose -f $COMPOSE_FILE logs -f dashboard"
echo "   Stop all:     docker compose -f $COMPOSE_FILE down"
echo "   Restart:      docker compose -f $COMPOSE_FILE restart dashboard"
echo "   Status:       docker compose -f $COMPOSE_FILE ps"
echo ""

echo -e "${GREEN}🎉 Happy deploying!${NC}"
