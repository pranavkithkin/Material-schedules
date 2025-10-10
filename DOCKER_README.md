# 🚀 Docker & Cloud Deployment - Quick Reference

## 📦 Files Created

1. **Dockerfile** - Multi-stage build for optimized image
2. **docker-compose.yml** - Development setup (SQLite)
3. **docker-compose.prod.yml** - Production setup (PostgreSQL + Redis)
4. **.dockerignore** - Files to exclude from Docker image
5. **.env.docker** - Environment template
6. **nginx/** - Reverse proxy configuration
7. **deploy.sh** - Automated deployment script
8. **setup-ssl.sh** - SSL certificate automation
9. **DEPLOYMENT_GUIDE.md** - Complete deployment documentation

---

## 🎯 Quick Start Guide

### Local Testing with Docker

```bash
# 1. Copy environment template
cp .env.docker .env

# 2. Edit .env with your API keys
nano .env

# 3. Build and run
docker compose up -d

# 4. Access
# Dashboard: http://localhost:5001
# n8n:       http://localhost:5678
```

### Production Deployment (VPS)

```bash
# 1. SSH to your VPS
ssh pkp@your-server-ip

# 2. Clone repository
git clone https://github.com/pranavkithkin/Material-schedules.git
cd Material-schedules

# 3. Run deployment script
chmod +x deploy.sh setup-ssl.sh
./deploy.sh

# 4. Configure SSL (after DNS is set up)
./setup-ssl.sh
```

---

## 🌥️ Recommended Cloud Provider: Hetzner

**Why Hetzner?**
- ✅ Best price/performance ratio
- ✅ €11.66/month for 2 vCPU, 8GB RAM, 80GB SSD
- ✅ Can host dashboard + n8n + 5-10 more projects
- ✅ Total cost: ~$13.60/month (vs $60-135/month with managed services)

**Sign up:** https://www.hetzner.com/cloud

---

## 📋 What's Included in Docker Setup

### Services:
1. **Dashboard** (Flask) - Your Material Delivery Dashboard
2. **PostgreSQL** - Production database
3. **Redis** - Cache and session management
4. **n8n** - Self-hosted automation (saves $20-60/month)
5. **Nginx** - Reverse proxy with SSL
6. **Certbot** - Free SSL certificates (Let's Encrypt)

### Features:
- ✅ Multi-stage Docker build (optimized image size)
- ✅ Health checks for all services
- ✅ Automatic SSL renewal
- ✅ Volume persistence for data
- ✅ Network isolation
- ✅ Production-ready security
- ✅ One-command deployment

---

## 🔧 Useful Commands

### Docker Compose

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f dashboard
docker compose logs -f n8n

# Restart a service
docker compose restart dashboard

# Check status
docker compose ps

# Update and rebuild
docker compose up -d --build

# Production deployment
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Database Operations

```bash
# Backup PostgreSQL
docker compose exec postgres pg_dump -U pkp_admin pkp_dashboard > backup.sql

# Restore PostgreSQL
docker compose exec -T postgres psql -U pkp_admin pkp_dashboard < backup.sql

# Access PostgreSQL
docker compose exec postgres psql -U pkp_admin -d pkp_dashboard
```

### Maintenance

```bash
# View resource usage
docker stats

# Clean up unused images
docker system prune -a

# View disk usage
docker system df

# Update images
docker compose pull
docker compose up -d
```

---

## 🔐 Security Checklist

- [ ] Change all default passwords in .env.production
- [ ] Use strong PostgreSQL password (32+ characters)
- [ ] Generate unique Flask secret key (64+ characters)
- [ ] Set up firewall (ufw) - only ports 80, 443, 22
- [ ] Disable root SSH login
- [ ] Use SSH keys (disable password authentication)
- [ ] Install fail2ban
- [ ] Configure automatic backups
- [ ] Set up monitoring (UptimeRobot)
- [ ] Obtain SSL certificates
- [ ] Regular security updates

---

## 💰 Cost Comparison

### Self-Hosted (Hetzner CX31)
- VPS: €11.66/month (~$12.60/month)
- Domain: ~$1/month
- SSL: FREE (Let's Encrypt)
- **Total: ~$13.60/month**

### Managed Services
- Heroku/Render: $25-50/month
- n8n.io: $20-60/month
- Database: $15-25/month
- **Total: $60-135/month**

### 🎉 Savings: $720-1,620/year with self-hosting!

---

## 📊 System Requirements

### Minimum (Development)
- 2 vCPU
- 4GB RAM
- 40GB SSD
- Example: Hetzner CX21 (€5.83/month)

### Recommended (Production)
- 2 vCPU
- 8GB RAM
- 80GB SSD
- Example: Hetzner CX31 (€11.66/month)

### Heavy Usage (Multiple Projects)
- 4 vCPU
- 16GB RAM
- 160GB SSD
- Example: Hetzner CX41 (€23.32/month)

---

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs dashboard

# Check environment variables
docker compose config

# Rebuild image
docker compose build --no-cache dashboard
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Verify credentials in .env.production
```

### SSL certificate issues
```bash
# Check certbot logs
docker compose logs certbot

# Verify DNS is pointing to server
dig dashboard.yourdomain.com

# Manual certificate request
docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d dashboard.yourdomain.com
```

### Nginx errors
```bash
# Test nginx config
docker compose exec nginx nginx -t

# Reload nginx
docker compose exec nginx nginx -s reload

# Check nginx logs
docker compose logs nginx
```

---

## 📚 Additional Resources

- **DEPLOYMENT_GUIDE.md** - Full deployment instructions
- **Docker Docs**: https://docs.docker.com
- **Docker Compose**: https://docs.docker.com/compose/
- **Hetzner Cloud**: https://docs.hetzner.com
- **n8n Self-Hosting**: https://docs.n8n.io/hosting/
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

## 🎯 Next Steps

1. Read DEPLOYMENT_GUIDE.md for detailed instructions
2. Choose your cloud provider (Hetzner recommended)
3. Deploy VPS and configure security
4. Clone repository and run deploy.sh
5. Configure DNS records
6. Run setup-ssl.sh for HTTPS
7. Set up automated backups
8. Configure monitoring

---

**Estimated setup time:** 2-3 hours for first deployment

**Difficulty:** Intermediate (scripts automate most steps)

**Support:** Check DEPLOYMENT_GUIDE.md or project documentation

---

**Created:** October 10, 2025
**Last Updated:** October 10, 2025
