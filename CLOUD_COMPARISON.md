# ☁️ Cloud Deployment - Quick Comparison

## TL;DR - Which Cloud Should I Choose?

### 🆓 Just Starting / Testing?
**Use Google Cloud Platform (GCP)**
- Get $300 FREE for 3 months
- No charges during trial
- Migrate to Hetzner after trial

### 💼 Ready for Production / Long-term?
**Use Hetzner Cloud**
- Only €11.66/month (~$12.60)
- Better value after GCP trial ends
- Can host multiple projects

---

## Detailed Comparison

| Feature | GCP Free Trial | Hetzner CX31 | DigitalOcean |
|---------|---------------|--------------|--------------|
| **Cost (First 3 months)** | FREE ($300 credits) | €35 (~$38) | ~$36-72 |
| **Cost (After 3 months)** | ~$25-50/month | €11.66/month | ~$12-24/month |
| **Initial Setup** | Free trial | Immediate charge | Immediate charge |
| **Resources** | 2-8GB RAM flexible | 8GB RAM, 2 vCPU | 4-8GB RAM |
| **Global Network** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐ Very Good |
| **Ease of Use** | ⭐⭐⭐ Medium | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Easy |
| **Free Tier** | After trial | None | None |
| **Documentation** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |

---

## 🎯 Recommended Strategy

### Phase 1: Testing & Development (Months 1-3)
**Use: Google Cloud Platform**
- Sign up for free trial
- Get $300 credits (3 months free)
- Deploy with `./deploy-gcp.sh`
- Test all features thoroughly
- **Cost: $0**

### Phase 2: Production (Month 4+)
**Option A: Stay on GCP**
- Convert to paid account
- Cost: ~$25-50/month
- Best if: You value GCP's global network and ecosystem

**Option B: Migrate to Hetzner** ⭐ RECOMMENDED
- Export data from GCP
- Deploy to Hetzner CX31
- Cost: €11.66/month (~$12.60)
- **Save: $150-450/year!**
- Best if: You want long-term cost savings

---

## 📋 Quick Start by Provider

### Google Cloud Platform

```bash
# 1. Sign up for free trial
open https://cloud.google.com/free

# 2. Install gcloud CLI (optional)
# Download from: https://cloud.google.com/sdk/docs/install

# 3. Run automated deployment
chmod +x deploy-gcp.sh
./deploy-gcp.sh

# Or follow manual guide
# See: DEPLOYMENT_GCP.md
```

**Estimated Setup Time:** 30-45 minutes  
**Deployment Guide:** [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md)

### Hetzner Cloud

```bash
# 1. Sign up for account
open https://console.hetzner.cloud

# 2. Create CX31 server (Ubuntu 22.04)

# 3. SSH and deploy
ssh root@your-server-ip
git clone https://github.com/pranavkithkin/Material-schedules.git
cd Material-schedules
chmod +x deploy.sh
./deploy.sh
```

**Estimated Setup Time:** 20-30 minutes  
**Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 💰 Total Cost of Ownership (1 Year)

### Scenario 1: GCP Only
- Months 1-3: $0 (free trial)
- Months 4-12: $25/month × 9 = $225
- **Total Year 1: $225**

### Scenario 2: GCP Trial → Hetzner
- Months 1-3: $0 (GCP free trial)
- Months 4-12: €11.66/month × 9 = €105 (~$113)
- **Total Year 1: $113** ⭐ BEST VALUE

### Scenario 3: Hetzner Only
- Months 1-12: €11.66/month × 12 = €140 (~$151)
- **Total Year 1: $151**

### Scenario 4: Managed Services (e.g., Heroku + n8n.io)
- Months 1-12: $60-135/month × 12 = $720-1,620
- **Total Year 1: $720-1,620** 💸 EXPENSIVE

---

## 🔄 Migration Guide (GCP → Hetzner)

When your GCP free trial ends, migrate to Hetzner:

### Step 1: Backup from GCP

```bash
# SSH into GCP VM
gcloud compute ssh pkp-dashboard-vm --zone=your-zone

# Backup database
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U pkp_admin pkp_dashboard > dashboard_backup.sql

# Backup uploads
tar -czf uploads_backup.tar.gz static/uploads/

# Download backups to local machine
gcloud compute scp pkp-dashboard-vm:~/dashboard_backup.sql ./ --zone=your-zone
gcloud compute scp pkp-dashboard-vm:~/uploads_backup.tar.gz ./ --zone=your-zone
```

### Step 2: Deploy to Hetzner

```bash
# Create Hetzner server (see DEPLOYMENT_GUIDE.md)

# SSH into new server
ssh root@hetzner-ip

# Deploy application
git clone https://github.com/pranavkithkin/Material-schedules.git
cd Material-schedules
./deploy.sh
```

### Step 3: Restore Data

```bash
# Upload backups to Hetzner
scp dashboard_backup.sql root@hetzner-ip:~/Material-schedules/
scp uploads_backup.tar.gz root@hetzner-ip:~/Material-schedules/

# SSH to Hetzner
ssh root@hetzner-ip
cd Material-schedules

# Restore database
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U pkp_admin pkp_dashboard < dashboard_backup.sql

# Restore uploads
tar -xzf uploads_backup.tar.gz
```

### Step 4: Update DNS

```bash
# Update A records to point to Hetzner IP
# dashboard.yourdomain.com → new-hetzner-ip
# n8n.yourdomain.com → new-hetzner-ip

# Wait for DNS propagation (5-60 minutes)

# Obtain new SSL certificates on Hetzner
./setup-ssl.sh
```

### Step 5: Cleanup GCP

```bash
# After verifying everything works on Hetzner:

# Stop GCP VM
gcloud compute instances stop pkp-dashboard-vm --zone=your-zone

# Wait a few days to ensure no issues

# Delete GCP VM (to stop all charges)
gcloud compute instances delete pkp-dashboard-vm --zone=your-zone
gcloud compute addresses delete pkp-dashboard-ip --region=your-region
```

---

## 🎓 Learning Resources

### Google Cloud Platform
- **Getting Started:** https://cloud.google.com/docs/get-started
- **Free Tier:** https://cloud.google.com/free/docs/free-cloud-features
- **Compute Engine:** https://cloud.google.com/compute/docs
- **Cost Calculator:** https://cloud.google.com/products/calculator

### Hetzner Cloud
- **Documentation:** https://docs.hetzner.com/cloud/
- **Community:** https://community.hetzner.com/
- **Status Page:** https://status.hetzner.com/
- **Tutorials:** https://community.hetzner.com/tutorials

### Docker & Deployment
- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **Let's Encrypt:** https://letsencrypt.org/docs/
- **n8n Self-Hosting:** https://docs.n8n.io/hosting/

---

## 📞 Support

### Deployment Issues
- Check: [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md) for GCP
- Check: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for Hetzner
- Check: [DOCKER_README.md](DOCKER_README.md) for Docker commands

### Cost Concerns
- **GCP Free Trial:** No charges for 3 months with $300 credits
- **Hetzner:** Predictable monthly billing, no surprises
- **Budget Alerts:** Set up in GCP Console or Hetzner Cloud

### Technical Support
- **GCP Support:** https://cloud.google.com/support
- **Hetzner Support:** https://console.hetzner.cloud/support
- **Community Help:** GitHub Issues or project documentation

---

**Last Updated:** October 10, 2025
