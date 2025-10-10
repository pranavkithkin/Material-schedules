#!/bin/bash

# 🔒 SSL Certificate Setup Script
# Run this AFTER your domain DNS is configured and pointing to your server

set -e

echo "🔒 SSL Certificate Setup"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Prompt for domains
read -p "Enter your dashboard domain (e.g., dashboard.pkpcontracting.com): " DASHBOARD_DOMAIN
read -p "Enter your n8n domain (e.g., n8n.pkpcontracting.com): " N8N_DOMAIN
read -p "Enter your email for Let's Encrypt notifications: " EMAIL

echo ""
echo "Domains to configure:"
echo "  Dashboard: $DASHBOARD_DOMAIN"
echo "  n8n: $N8N_DOMAIN"
echo "  Email: $EMAIL"
echo ""
read -p "Is this correct? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Update nginx configuration files
echo "📝 Updating nginx configuration..."

# Update dashboard.conf
sed -i "s/dashboard.yourdomain.com/$DASHBOARD_DOMAIN/g" nginx/conf.d/dashboard.conf

# Update n8n.conf
sed -i "s/n8n.yourdomain.com/$N8N_DOMAIN/g" nginx/conf.d/n8n.conf

echo -e "${GREEN}✅ Nginx configuration updated${NC}"
echo ""

# Temporarily disable SSL in nginx configs for initial certificate request
echo "🔧 Preparing nginx for certificate request..."

# Create temporary HTTP-only configs
cp nginx/conf.d/dashboard.conf nginx/conf.d/dashboard.conf.ssl
cp nginx/conf.d/n8n.conf nginx/conf.d/n8n.conf.ssl

# Create simple HTTP configs for certbot
cat > nginx/conf.d/dashboard.conf << EOF
server {
    listen 80;
    server_name $DASHBOARD_DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://dashboard:5001;
    }
}
EOF

cat > nginx/conf.d/n8n.conf << EOF
server {
    listen 80;
    server_name $N8N_DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://n8n:5678;
    }
}
EOF

# Restart nginx with HTTP-only configs
echo "🔄 Restarting nginx..."
docker compose -f docker-compose.prod.yml restart nginx
sleep 3

echo ""
echo "📜 Obtaining SSL certificate for dashboard..."

docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d "$DASHBOARD_DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email

echo -e "${GREEN}✅ Dashboard certificate obtained${NC}"
echo ""

echo "📜 Obtaining SSL certificate for n8n..."

docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d "$N8N_DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email

echo -e "${GREEN}✅ n8n certificate obtained${NC}"
echo ""

# Restore SSL-enabled configs
echo "🔧 Enabling SSL in nginx..."
mv nginx/conf.d/dashboard.conf.ssl nginx/conf.d/dashboard.conf
mv nginx/conf.d/n8n.conf.ssl nginx/conf.d/n8n.conf

# Restart nginx with SSL
echo "🔄 Restarting nginx with SSL..."
docker compose -f docker-compose.prod.yml restart nginx
sleep 3

echo ""
echo "🧪 Testing SSL configuration..."

# Test dashboard
if curl -sI "https://$DASHBOARD_DOMAIN" | grep -q "200 OK"; then
    echo -e "${GREEN}✅ Dashboard SSL working${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard SSL might need time to propagate${NC}"
fi

# Test n8n
if curl -sI "https://$N8N_DOMAIN" | grep -q "200"; then
    echo -e "${GREEN}✅ n8n SSL working${NC}"
else
    echo -e "${YELLOW}⚠️  n8n SSL might need time to propagate${NC}"
fi

echo ""
echo "🧪 Testing certificate renewal..."
docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

echo ""
echo "=============================================="
echo -e "${GREEN}✅ SSL Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "🌐 Your sites are now secured with HTTPS:"
echo "   Dashboard: https://$DASHBOARD_DOMAIN"
echo "   n8n:       https://$N8N_DOMAIN"
echo ""
echo "📋 Certificates will auto-renew every 60 days"
echo ""
echo "🔍 Test your SSL rating at:"
echo "   https://www.ssllabs.com/ssltest/analyze.html?d=$DASHBOARD_DOMAIN"
echo ""
