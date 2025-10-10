# 🚀 Complete Deployment Guide
## Material Delivery Dashboard - Docker & Cloud Deployment

---

## 📋 Table of Contents
1. [Cloud Provider Recommendations](#cloud-provider-recommendations)
2. [VPS Setup](#vps-setup)
3. [Docker Deployment](#docker-deployment)
4. [Domain & SSL Configuration](#domain--ssl-configuration)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Cost Estimation](#cost-estimation)

---

## 🌥️ Cloud Provider Recommendations

### **BEST FOR YOU: Hetzner Cloud** ⭐ RECOMMENDED
**Why Hetzner?**
- ✅ **Excellent Price/Performance** - Best value in the market
- ✅ **Multiple Projects** - Can host n8n, dashboard, and hobby projects
- ✅ **European Data Centers** - Close to UAE, good latency
- ✅ **Simple Pricing** - No hidden costs, predictable billing
- ✅ **Great Community** - Excellent documentation and support

**Pricing:**
- **CX21** (2 vCPU, 4GB RAM, 40GB SSD): €5.83/month (~$6.30/month)
  - Perfect for: Dashboard + n8n + 2-3 small projects
- **CX31** (2 vCPU, 8GB RAM, 80GB SSD): €11.66/month (~$12.60/month)
  - Perfect for: Dashboard + n8n + 5-10 projects + room to grow

**Website:** https://www.hetzner.com/cloud

---

### Alternative Options:

#### **DigitalOcean** - Developer-Friendly
- **Droplet**: $12-24/month (2-4GB RAM)
- **Pros**: Great documentation, managed databases available, 1-click apps
- **Cons**: More expensive than Hetzner
- **Best for**: If you want managed services

#### **Vultr** - Global Coverage
- **Cloud Compute**: $6-12/month (2-4GB RAM)
- **Pros**: 25 data centers worldwide, good for global projects
- **Cons**: Less features than competitors
- **Best for**: If you need specific regional coverage

#### **Linode (Akamai)** - Reliable
- **Shared CPU**: $12-24/month (2-4GB RAM)
- **Pros**: Very reliable, good support, backups included
- **Cons**: Slightly more expensive
- **Best for**: Mission-critical applications

#### **Oracle Cloud Free Tier** - Budget Option
- **Always Free**: 4 ARM CPUs, 24GB RAM (yes, really free!)
- **Pros**: Completely free forever, generous resources
- **Cons**: ARM architecture (Docker images must support ARM), UI can be complex
- **Best for**: Learning, testing, non-critical projects

#### **Contabo** - Maximum Resources
- **VPS**: €6.99/month (4 vCPU, 8GB RAM, 200GB SSD)
- **Pros**: Tons of resources for the price
- **Cons**: Slower network, less reliable support
- **Best for**: Heavy workloads on tight budget

---

## 🎯 MY RECOMMENDATION FOR YOU

### **Setup: Hetzner CX31 (€11.66/month)**

**What you can host:**
1. ✅ Material Delivery Dashboard (Flask)
2. ✅ n8n Automation Platform (self-hosted)
3. ✅ 5-10 additional hobby/office projects
4. ✅ PostgreSQL Database
5. ✅ Redis Cache
6. ✅ Nginx Reverse Proxy
7. ✅ SSL Certificates (Let's Encrypt - Free)

**Total Monthly Cost:**
- VPS: €11.66 (~$12.60)
- Domain: ~$12/year (~$1/month)
- **Total: ~$13.60/month** (all-inclusive!)

---

## 🛠️ VPS Setup

### Step 1: Create Hetzner Account & Deploy Server

```bash
# 1. Go to: https://console.hetzner.cloud
# 2. Create new project: "PKP-Production"
# 3. Create server:
#    - Location: Falkenstein, Germany (closest to UAE with good connectivity)
#    - Image: Ubuntu 22.04 LTS
#    - Type: CX31 (2 vCPU, 8GB RAM, 80GB SSD)
#    - Networking: Enable IPv4 & IPv6
#    - SSH Key: Add your public key
#    - Name: pkp-production-01
```

### Step 2: Initial Server Configuration

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose V2
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Create non-root user
adduser pkp
usermod -aG docker pkp
usermod -aG sudo pkp

# Switch to new user
su - pkp
```

### Step 3: Security Hardening

```bash
# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no
sudo systemctl restart sshd

# Install fail2ban (brute force protection)
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🐳 Docker Deployment

### Step 1: Clone Your Repository

```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Clone your repository
git clone https://github.com/pranavkithkin/Material-schedules.git
cd Material-schedules

# Create production environment file
cp .env.docker .env.production
nano .env.production
# Fill in your actual values
```

### Step 2: Configure Production Environment

```bash
# Generate secure secrets
# Flask secret key (64 characters)
openssl rand -hex 32

# n8n encryption key (minimum 10 characters)
openssl rand -hex 16

# PostgreSQL password
openssl rand -base64 32

# Redis password
openssl rand -base64 24

# Update .env.production with these values
```

### Step 3: Deploy with Docker Compose

```bash
# Development deployment (SQLite, for testing)
docker compose up -d

# Production deployment (PostgreSQL, recommended)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# Check status
docker compose ps

# View logs
docker compose logs -f dashboard
docker compose logs -f n8n

# Check health
curl http://localhost:5001/
curl http://localhost:5678/
```

### Step 4: Database Migration (First Time Only)

```bash
# For production with PostgreSQL
docker compose -f docker-compose.prod.yml exec dashboard python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database tables created!')
"
```

---

## 🌐 Domain & SSL Configuration

### Step 1: Purchase Domain

**Recommended Registrars:**
- **Namecheap**: $8-12/year (.com)
- **Cloudflare**: At-cost pricing (~$10/year)
- **GoDaddy**: $12-20/year (more expensive)

**Example domains:**
- `pkpcontracting.com`
- `pkpdashboard.com`
- `pkpoffice.com`

### Step 2: Configure DNS (Cloudflare Recommended)

```bash
# Add A records pointing to your VPS IP:

# Type  | Name       | Content          | TTL  | Proxy
# ------|------------|------------------|------|-------
# A     | @          | YOUR_SERVER_IP   | Auto | Proxied
# A     | dashboard  | YOUR_SERVER_IP   | Auto | Proxied
# A     | n8n        | YOUR_SERVER_IP   | Auto | Proxied
# A     | www        | YOUR_SERVER_IP   | Auto | Proxied

# Example:
# dashboard.pkpcontracting.com → 88.198.45.123
# n8n.pkpcontracting.com       → 88.198.45.123
```

### Step 3: Update Nginx Configuration

```bash
# Update domain names in nginx config files
cd ~/projects/Material-schedules/nginx/conf.d

# Edit dashboard.conf
nano dashboard.conf
# Replace: dashboard.yourdomain.com → dashboard.pkpcontracting.com

# Edit n8n.conf
nano n8n.conf
# Replace: n8n.yourdomain.com → n8n.pkpcontracting.com
```

### Step 4: Obtain SSL Certificates (Let's Encrypt)

```bash
# First, start nginx without SSL temporarily
# Modify nginx configs to comment out SSL lines temporarily

# Obtain certificates for dashboard
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d dashboard.pkpcontracting.com \
  --email your-email@gmail.com \
  --agree-tos \
  --no-eff-email

# Obtain certificates for n8n
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d n8n.pkpcontracting.com \
  --email your-email@gmail.com \
  --agree-tos \
  --no-eff-email

# Restart nginx with SSL enabled
docker compose -f docker-compose.prod.yml restart nginx

# Test auto-renewal
docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run
```

### Step 5: Verify Deployment

```bash
# Test HTTP to HTTPS redirect
curl -I http://dashboard.pkpcontracting.com
# Should return: 301 Moved Permanently

# Test HTTPS
curl -I https://dashboard.pkpcontracting.com
# Should return: 200 OK

# Test n8n
curl -I https://n8n.pkpcontracting.com
# Should return: 200 OK (with basic auth prompt)

# Check SSL rating
# Visit: https://www.ssllabs.com/ssltest/
# Enter your domain - should get A or A+ rating
```

---

## 📊 Monitoring & Maintenance

### Daily Health Checks

```bash
# Check container status
docker compose ps

# Check resource usage
docker stats

# Check disk space
df -h

# Check logs for errors
docker compose logs --tail=50 dashboard
docker compose logs --tail=50 n8n
```

### Automatic Backups

```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash

# Backup PostgreSQL
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U pkp_admin pkp_dashboard | gzip > /backups/dashboard_$(date +%Y%m%d).sql.gz

# Backup n8n data
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U pkp_admin n8n | gzip > /backups/n8n_$(date +%Y%m%d).sql.gz

# Backup uploaded files
tar -czf /backups/uploads_$(date +%Y%m%d).tar.gz /home/pkp/projects/Material-schedules/static/uploads/

# Delete backups older than 30 days
find /backups -name "*.gz" -mtime +30 -delete

echo "Backup completed: $(date)"
EOF

chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/pkp/backup.sh >> /var/log/backup.log 2>&1
```

### Update Deployment

```bash
# Pull latest code
cd ~/projects/Material-schedules
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml build --no-cache dashboard
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f dashboard
```

---

## 💰 Cost Estimation

### Hetzner CX31 Setup (RECOMMENDED)

| Item | Cost | Notes |
|------|------|-------|
| **VPS (CX31)** | €11.66/month | 2 vCPU, 8GB RAM, 80GB SSD |
| **Domain** | ~$1/month | $12/year average |
| **SSL Certificate** | FREE | Let's Encrypt |
| **Backups** | FREE | DIY with scripts |
| **Total** | **~$13.60/month** | **~$163/year** |

### What You Get:
✅ Material Delivery Dashboard (production-ready)
✅ Self-hosted n8n (no $20-60/month n8n.io fees)
✅ Host 5-10 additional small projects
✅ PostgreSQL database with backups
✅ SSL certificates with auto-renewal
✅ Nginx reverse proxy
✅ Full control and customization

### Comparison with Managed Services:

| Service | Managed SaaS | Self-Hosted (Hetzner) | Savings |
|---------|--------------|----------------------|---------|
| n8n | $20-60/month | Included | **$240-720/year** |
| Heroku/Render | $25-50/month | Included | **$300-600/year** |
| Database | $15-25/month | Included | **$180-300/year** |
| **Total** | **$60-135/month** | **$13.60/month** | **$720-1,620/year** 🎉 |

---

## 🚀 Quick Start Commands

### Initial Deployment
```bash
# 1. SSH to server
ssh pkp@your-server-ip

# 2. Clone repo
git clone https://github.com/pranavkithkin/Material-schedules.git
cd Material-schedules

# 3. Configure environment
cp .env.docker .env.production
nano .env.production  # Fill in your values

# 4. Deploy
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# 5. Check status
docker compose ps
```

### Daily Operations
```bash
# View logs
docker compose logs -f dashboard

# Restart service
docker compose restart dashboard

# Update deployment
git pull && docker compose up -d --build

# Database backup
docker compose exec postgres pg_dump -U pkp_admin pkp_dashboard > backup.sql
```

---

## 📞 Support & Resources

### Hetzner Resources:
- **Console**: https://console.hetzner.cloud
- **Docs**: https://docs.hetzner.com
- **Community**: https://community.hetzner.com
- **Status**: https://status.hetzner.com

### Docker Resources:
- **Docs**: https://docs.docker.com
- **Compose**: https://docs.docker.com/compose/
- **Hub**: https://hub.docker.com

### n8n Resources:
- **Docs**: https://docs.n8n.io
- **Self-Hosting**: https://docs.n8n.io/hosting/
- **Community**: https://community.n8n.io

---

## 🎯 Next Steps

1. ✅ Sign up for Hetzner Cloud
2. ✅ Deploy CX31 server (Ubuntu 22.04)
3. ✅ Configure SSH and security
4. ✅ Install Docker and Docker Compose
5. ✅ Purchase domain name
6. ✅ Configure DNS records
7. ✅ Clone repository to server
8. ✅ Configure .env.production
9. ✅ Deploy with docker-compose.prod.yml
10. ✅ Obtain SSL certificates
11. ✅ Test deployment
12. ✅ Set up backups
13. ✅ Configure monitoring

**Estimated Setup Time: 2-3 hours**

---

## ⚠️ Important Notes

1. **Backups**: Always maintain offsite backups
2. **Security**: Keep all passwords strong and unique
3. **Updates**: Regularly update Docker images and system packages
4. **Monitoring**: Set up uptime monitoring (e.g., UptimeRobot - free)
5. **Costs**: Hetzner bills monthly, no hidden fees
6. **Scaling**: Easy to upgrade to larger VPS when needed

---

**Need help?** Contact Pranav or check the project documentation.

**Last Updated:** October 10, 2025
