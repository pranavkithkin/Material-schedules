# 🌐 Google Cloud Platform (GCP) Deployment Guide
## Material Delivery Dashboard - Complete Setup with $300 Free Credits

---

## 🎁 GCP Free Trial Benefits

**What You Get:**
- ✅ **$300 free credits** valid for 90 days (3 months)
- ✅ **No automatic charges** after trial ends
- ✅ **Full GCP access** - all services available
- ✅ **Always Free tier** continues after credits expire
- ✅ **Global infrastructure** - 200+ locations worldwide

**Sign Up:** https://cloud.google.com/free

---

## 💰 Cost Estimation for Your Project

### Option 1: e2-small (Recommended for Testing)
- **Instance**: e2-small (2 vCPU, 2GB RAM)
- **Storage**: 20GB Standard Persistent Disk
- **Cost**: ~$13/month (covered by free credits)
- **Good for**: Testing, development, light production

### Option 2: e2-medium (Recommended for Production)
- **Instance**: e2-medium (2 vCPU, 4GB RAM)
- **Storage**: 30GB Standard Persistent Disk
- **Cost**: ~$25/month (covered by free credits)
- **Good for**: Production, multiple projects, heavier workloads

### Option 3: e2-standard-2 (Heavy Production)
- **Instance**: e2-standard-2 (2 vCPU, 8GB RAM)
- **Storage**: 50GB Standard Persistent Disk
- **Cost**: ~$50/month (covered by free credits)
- **Good for**: Dashboard + n8n + 10+ projects

### Always Free Tier (After Credits)
- **e2-micro**: 1 shared vCPU, 1GB RAM - FREE forever
- **Storage**: 30GB Standard Persistent Disk - FREE
- **Networking**: 1GB egress to most regions/month - FREE
- **Good for**: Small hobby projects (but might be tight for your dashboard)

**All options are FREE for 3 months with $300 credits!**

---

## 🚀 Complete Deployment Steps

### Step 1: Create GCP Account & Project

1. **Sign up for GCP Free Trial**
   - Go to: https://console.cloud.google.com
   - Click "Start Free" or "Try Free"
   - Enter payment details (won't be charged during trial)
   - Accept terms and verify identity

2. **Create New Project**
   ```
   Project Name: pkp-material-dashboard
   Project ID: pkp-dashboard-[random-id]
   Location: No organization
   ```

3. **Enable Required APIs**
   - Go to: APIs & Services > Enable APIs
   - Enable: Compute Engine API
   - Enable: Cloud SQL Admin API (if using managed database)

### Step 2: Create VM Instance

#### Option A: Using GCP Console (GUI)

1. **Navigate to Compute Engine**
   - Go to: Compute Engine > VM instances
   - Click "Create Instance"

2. **Configure Instance**
   ```
   Name: pkp-dashboard-vm
   Region: us-central1 (Iowa) - closest to UAE with good pricing
           OR asia-south1 (Mumbai) - closer to UAE
   Zone: us-central1-a (or asia-south1-a)
   
   Machine Configuration:
   - Series: E2
   - Machine type: e2-medium (2 vCPU, 4GB memory)
   
   Boot Disk:
   - Click "Change"
   - Operating System: Ubuntu
   - Version: Ubuntu 22.04 LTS
   - Boot disk type: Standard persistent disk
   - Size: 30GB
   
   Firewall:
   ✓ Allow HTTP traffic
   ✓ Allow HTTPS traffic
   
   Advanced Options > Networking:
   - Network tags: http-server, https-server
   ```

3. **Click "Create"**

#### Option B: Using gcloud CLI (Faster)

```bash
# Install Google Cloud SDK first
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project pkp-dashboard-[your-project-id]

# Create VM instance
gcloud compute instances create pkp-dashboard-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose git
    systemctl enable docker
    systemctl start docker'

# Create firewall rules if not exist
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --target-tags http-server \
  --description "Allow HTTP traffic"

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --target-tags https-server \
  --description "Allow HTTPS traffic"
```

### Step 3: Configure Firewall Rules

```bash
# In GCP Console: VPC Network > Firewall

# Create rule for Flask (if needed for testing)
gcloud compute firewall-rules create allow-flask \
  --allow tcp:5001 \
  --target-tags http-server \
  --description "Allow Flask development server"

# Create rule for n8n (if accessing directly)
gcloud compute firewall-rules create allow-n8n \
  --allow tcp:5678 \
  --target-tags http-server \
  --description "Allow n8n access"
```

### Step 4: Connect to VM and Install Docker

```bash
# Get external IP
gcloud compute instances list

# SSH into VM (from GCP Console or CLI)
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a

# Once connected, update system
sudo apt update && sudo apt upgrade -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose V2
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version

# Add current user to docker group
sudo usermod -aG docker $USER

# Exit and reconnect for group changes
exit

# SSH back in
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a
```

### Step 5: Deploy Your Application

```bash
# Clone repository
git clone https://github.com/pranavkithkin/Material-schedules.git
cd Material-schedules

# Create production environment file
cp .env.docker .env.production

# Edit environment variables
nano .env.production
# Fill in all required values (API keys, passwords, etc.)

# Generate secure secrets
openssl rand -hex 32  # Flask secret
openssl rand -hex 16  # n8n encryption
openssl rand -base64 32  # PostgreSQL password

# Make scripts executable
chmod +x deploy.sh setup-ssl.sh

# Run deployment script
./deploy.sh
# Select option 2 (Production)

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f dashboard
```

### Step 6: Configure Static IP Address

```bash
# Reserve static external IP
gcloud compute addresses create pkp-dashboard-ip \
  --region=us-central1

# Get the IP address
gcloud compute addresses list

# Attach to VM
gcloud compute instances delete-access-config pkp-dashboard-vm \
  --access-config-name="External NAT" \
  --zone=us-central1-a

gcloud compute instances add-access-config pkp-dashboard-vm \
  --access-config-name="External NAT" \
  --address=pkp-dashboard-ip \
  --zone=us-central1-a
```

### Step 7: Configure Domain & DNS

1. **Purchase Domain** (if you don't have one)
   - Use: Namecheap, Cloudflare, Google Domains
   - Cost: ~$12/year

2. **Configure DNS Records**
   ```
   Type  | Name       | Value (Your GCP IP)  | TTL
   ------|------------|---------------------|-----
   A     | @          | 34.123.45.67        | 3600
   A     | dashboard  | 34.123.45.67        | 3600
   A     | n8n        | 34.123.45.67        | 3600
   A     | www        | 34.123.45.67        | 3600
   ```

3. **Wait for DNS Propagation** (5-60 minutes)
   ```bash
   # Check if DNS is ready
   dig dashboard.yourdomain.com
   nslookup dashboard.yourdomain.com
   ```

### Step 8: Setup SSL Certificates

```bash
# Update nginx configs with your domain
cd ~/Material-schedules
nano nginx/conf.d/dashboard.conf
# Replace: dashboard.yourdomain.com with your actual domain

nano nginx/conf.d/n8n.conf
# Replace: n8n.yourdomain.com with your actual domain

# Run SSL setup script
./setup-ssl.sh
# Follow prompts and enter your domains

# Verify HTTPS
curl -I https://dashboard.yourdomain.com
curl -I https://n8n.yourdomain.com
```

---

## 🔒 Security Best Practices for GCP

### 1. Configure Firewall (Network Security)

```bash
# List current firewall rules
gcloud compute firewall-rules list

# Remove unnecessary ports
# Only keep: 22 (SSH), 80 (HTTP), 443 (HTTPS)

# Restrict SSH to your IP
gcloud compute firewall-rules update default-allow-ssh \
  --source-ranges=YOUR_HOME_IP/32
```

### 2. Setup IAM & Service Accounts

```bash
# Create service account for your app
gcloud iam service-accounts create pkp-dashboard-sa \
  --display-name="PKP Dashboard Service Account"

# Grant minimal permissions
gcloud projects add-iam-policy-binding pkp-dashboard-[project-id] \
  --member="serviceAccount:pkp-dashboard-sa@pkp-dashboard-[project-id].iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### 3. Enable OS Login (Better than SSH keys)

```bash
# Enable OS Login
gcloud compute project-info add-metadata \
  --metadata enable-oslogin=TRUE

# Connect using OS Login
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a
```

### 4. Setup Automatic Backups

```bash
# Create snapshot schedule
gcloud compute resource-policies create snapshot-schedule pkp-daily-backup \
  --region=us-central1 \
  --max-retention-days=7 \
  --on-source-disk-delete=keep-auto-snapshots \
  --daily-schedule \
  --start-time=02:00

# Attach to disk
gcloud compute disks add-resource-policies pkp-dashboard-vm \
  --resource-policies=pkp-daily-backup \
  --zone=us-central1-a
```

---

## 📊 GCP Monitoring & Logging

### Setup Monitoring

1. **Enable Cloud Monitoring**
   - Go to: Monitoring > Dashboards
   - Create custom dashboard for your VM

2. **Setup Uptime Checks**
   ```bash
   # In GCP Console: Monitoring > Uptime checks
   - Name: PKP Dashboard Health
   - Protocol: HTTPS
   - Resource: dashboard.yourdomain.com
   - Path: /health
   - Check frequency: 1 minute
   ```

3. **Create Alerts**
   - CPU > 80% for 5 minutes
   - Memory > 90% for 5 minutes
   - Disk > 85% used
   - HTTP uptime check fails

### View Logs

```bash
# View VM logs
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=[INSTANCE_ID]" \
  --limit=50 \
  --format=json

# Or use Console: Logging > Logs Explorer
```

---

## 💾 Backup Strategy

### Option 1: Manual Backups

```bash
# Create snapshot
gcloud compute disks snapshot pkp-dashboard-vm \
  --snapshot-names=pkp-backup-$(date +%Y%m%d) \
  --zone=us-central1-a

# List snapshots
gcloud compute snapshots list

# Restore from snapshot (if needed)
gcloud compute disks create pkp-dashboard-vm-restored \
  --source-snapshot=pkp-backup-20251010 \
  --zone=us-central1-a
```

### Option 2: Automated Database Backups

```bash
# Inside VM, create backup script
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose -f ~/Material-schedules/docker-compose.prod.yml exec -T postgres \
  pg_dump -U pkp_admin pkp_dashboard | \
  gzip > $BACKUP_DIR/dashboard_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup n8n
docker compose -f ~/Material-schedules/docker-compose.prod.yml exec -T postgres \
  pg_dump -U pkp_admin n8n | \
  gzip > $BACKUP_DIR/n8n_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$(date +%Y%m%d_%H%M%S).tar.gz \
  ~/Material-schedules/static/uploads/

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $(date)"
EOF

chmod +x ~/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/[your-username]/backup-db.sh >> /var/log/backup.log 2>&1
```

### Option 3: Sync Backups to Cloud Storage

```bash
# Create Cloud Storage bucket
gsutil mb -l us-central1 gs://pkp-dashboard-backups

# Install gsutil (usually pre-installed on GCP VMs)

# Create sync script
cat > ~/sync-to-gcs.sh << 'EOF'
#!/bin/bash
gsutil -m rsync -r -d /home/$USER/backups gs://pkp-dashboard-backups/
echo "Synced backups to GCS: $(date)"
EOF

chmod +x ~/sync-to-gcs.sh

# Add to crontab (daily at 3 AM, after backup)
crontab -e
# Add: 0 3 * * * /home/[your-username]/sync-to-gcs.sh >> /var/log/gcs-sync.log 2>&1
```

---

## 📈 Scaling & Optimization

### Upgrade VM Instance

```bash
# Stop VM
gcloud compute instances stop pkp-dashboard-vm --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type pkp-dashboard-vm \
  --machine-type=e2-standard-2 \
  --zone=us-central1-a

# Start VM
gcloud compute instances start pkp-dashboard-vm --zone=us-central1-a
```

### Add More Storage

```bash
# Create new disk
gcloud compute disks create pkp-data-disk \
  --size=50GB \
  --zone=us-central1-a

# Attach to VM
gcloud compute instances attach-disk pkp-dashboard-vm \
  --disk=pkp-data-disk \
  --zone=us-central1-a

# SSH into VM and mount
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a

# Format and mount
sudo mkfs.ext4 /dev/sdb
sudo mkdir /mnt/data
sudo mount /dev/sdb /mnt/data
echo "/dev/sdb /mnt/data ext4 defaults 0 0" | sudo tee -a /etc/fstab
```

---

## 💰 Cost Management

### Track Spending

1. **Set Budget Alerts**
   - Go to: Billing > Budgets & alerts
   - Create budget: $50/month
   - Alert at: 50%, 90%, 100%

2. **View Cost Breakdown**
   - Go to: Billing > Reports
   - Filter by: Service, Project, Time range

### Optimize Costs

```bash
# Use preemptible VMs (up to 80% cheaper, but can be terminated)
gcloud compute instances create pkp-dashboard-vm-preemptible \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --preemptible \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud

# Stop VM when not in use (saves compute costs)
gcloud compute instances stop pkp-dashboard-vm --zone=us-central1-a

# Start when needed
gcloud compute instances start pkp-dashboard-vm --zone=us-central1-a
```

---

## 🎯 Quick Command Reference

### SSH & Access

```bash
# SSH into VM
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a

# Copy files to VM
gcloud compute scp local-file.txt pkp-dashboard-vm:~/ --zone=us-central1-a

# Copy files from VM
gcloud compute scp pkp-dashboard-vm:~/remote-file.txt ./ --zone=us-central1-a

# Run command on VM
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a --command="docker compose ps"
```

### VM Management

```bash
# List instances
gcloud compute instances list

# Stop instance
gcloud compute instances stop pkp-dashboard-vm --zone=us-central1-a

# Start instance
gcloud compute instances start pkp-dashboard-vm --zone=us-central1-a

# Restart instance
gcloud compute instances reset pkp-dashboard-vm --zone=us-central1-a

# Delete instance (careful!)
gcloud compute instances delete pkp-dashboard-vm --zone=us-central1-a
```

### Docker Management (on VM)

```bash
# View running containers
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f dashboard

# Restart service
docker compose -f docker-compose.prod.yml restart dashboard

# Update deployment
cd ~/Material-schedules
git pull
docker compose -f docker-compose.prod.yml up -d --build

# Backup database
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U pkp_admin pkp_dashboard > backup.sql
```

---

## 🆘 Troubleshooting

### VM Won't Start

```bash
# Check VM status
gcloud compute instances describe pkp-dashboard-vm --zone=us-central1-a

# View serial console logs
gcloud compute instances get-serial-port-output pkp-dashboard-vm --zone=us-central1-a
```

### Can't SSH into VM

```bash
# Reset SSH keys
gcloud compute config-ssh

# Try browser SSH from Console
# Go to: Compute Engine > VM instances > SSH (dropdown) > Open in browser window
```

### Out of Disk Space

```bash
# SSH into VM
gcloud compute ssh pkp-dashboard-vm --zone=us-central1-a

# Check disk usage
df -h

# Clean up Docker
docker system prune -a
docker volume prune

# Increase disk size
gcloud compute disks resize pkp-dashboard-vm --size=50GB --zone=us-central1-a

# Resize filesystem (on VM)
sudo growpart /dev/sda 1
sudo resize2fs /dev/sda1
```

### High Costs

```bash
# Check what's consuming credits
# Go to: Billing > Reports
# Sort by: Cost

# Common culprits:
# - VM running 24/7 (consider stopping when not needed)
# - Large disk space (reduce if possible)
# - High egress traffic (optimize data transfer)
```

---

## 📋 Post-Deployment Checklist

- [ ] VM instance created and running
- [ ] Docker and Docker Compose installed
- [ ] Application deployed and accessible
- [ ] Static IP address reserved and attached
- [ ] Domain DNS configured and propagated
- [ ] SSL certificates obtained and working
- [ ] Firewall rules configured (only 22, 80, 443)
- [ ] Automatic backups scheduled
- [ ] Cloud Storage sync configured
- [ ] Monitoring and alerts set up
- [ ] Budget alerts configured
- [ ] Test all features work correctly
- [ ] Document any custom configurations

---

## 🎉 Success!

Your Material Delivery Dashboard is now running on Google Cloud Platform!

**Access URLs:**
- Dashboard: https://dashboard.yourdomain.com
- n8n: https://n8n.yourdomain.com

**Free Trial Benefits:**
- $300 credits for 3 months
- After trial: Move to Always Free tier (e2-micro) or pay-as-you-go
- Estimated cost after trial: $25-50/month (or free with e2-micro)

**Support:**
- GCP Console: https://console.cloud.google.com
- GCP Documentation: https://cloud.google.com/docs
- GCP Support: https://cloud.google.com/support

---

## 🔄 After Free Trial Ends

### Option 1: Continue on GCP (Pay-as-you-go)
- Upgrade to paid account
- Keep same VM and configuration
- Cost: ~$25-50/month for e2-medium

### Option 2: Migrate to Hetzner (Cheaper)
- Export data from GCP
- Deploy to Hetzner VPS (€11.66/month)
- Save $10-30/month ongoing

### Option 3: Downgrade to Always Free Tier
- Change to e2-micro (1 shared vCPU, 1GB RAM)
- Free forever, but limited resources
- Might be tight for dashboard + n8n

---

**Created:** October 10, 2025  
**Last Updated:** October 10, 2025
