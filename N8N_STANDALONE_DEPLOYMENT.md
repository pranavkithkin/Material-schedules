# 🤖 Standalone n8n Deployment on GCP
## Self-hosted n8n Automation Platform - 24/7 Access

---

## 🎯 Why Deploy n8n Separately?

**Benefits of Standalone Deployment:**
- ✅ **Isolation** - n8n issues don't affect your dashboard
- ✅ **Easier Scaling** - Scale n8n independently
- ✅ **Simpler Backups** - Backup only n8n data
- ✅ **Resource Control** - Dedicate resources to n8n
- ✅ **Multiple Projects** - One n8n can serve multiple projects

---

## 💰 Cost Estimation

### Option 1: Small Instance (Recommended)
- **Instance**: e2-small (2 vCPU, 2GB RAM)
- **Storage**: 20GB Standard Persistent Disk
- **Cost**: ~$13/month (FREE for 3 months with GCP credits)
- **Good for**: Personal use, light automation, 5-10 workflows

### Option 2: Medium Instance (For Heavy Use)
- **Instance**: e2-medium (2 vCPU, 4GB RAM)
- **Storage**: 30GB Standard Persistent Disk
- **Cost**: ~$25/month (FREE for 3 months)
- **Good for**: Business use, complex workflows, 20+ workflows

---

## 🚀 Complete Deployment Steps

### Step 1: Create GCP VM for n8n

#### Using GCP Console (GUI):

1. **Go to Compute Engine**
   - Navigate to: https://console.cloud.google.com
   - Compute Engine > VM instances
   - Click "Create Instance"

2. **Configure VM:**
   ```
   Name: n8n-server
   Region: us-central1 (Iowa) OR asia-south1 (Mumbai - closer to UAE)
   Zone: us-central1-a (or asia-south1-a)
   
   Machine Configuration:
   - Series: E2
   - Machine type: e2-small (2 vCPU, 2GB RAM)
   
   Boot Disk:
   - Operating System: Ubuntu
   - Version: Ubuntu 22.04 LTS
   - Boot disk type: Standard persistent disk
   - Size: 20GB
   
   Firewall:
   ✓ Allow HTTP traffic
   ✓ Allow HTTPS traffic
   
   Network tags: http-server, https-server
   ```

3. **Click "Create"**

#### Using gcloud CLI (Faster):

```bash
# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create VM
gcloud compute instances create n8n-server \
  --zone=us-central1-a \
  --machine-type=e2-small \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y docker.io git
    systemctl enable docker
    systemctl start docker'

# Create firewall rules
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --target-tags http-server \
  --description "Allow HTTP traffic"

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --target-tags https-server \
  --description "Allow HTTPS traffic"
```

---

### Step 2: Reserve Static IP

```bash
# Reserve static IP
gcloud compute addresses create n8n-ip \
  --region=us-central1

# Get the IP address
gcloud compute addresses list

# Note the IP address (e.g., 34.123.45.67)
```

---

### Step 3: SSH into Server

```bash
# SSH to server
gcloud compute ssh n8n-server --zone=us-central1-a

# Or use browser SSH from GCP Console
```

---

### Step 4: Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose V2
sudo apt install docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker compose version

# Exit and reconnect for group changes to take effect
exit

# SSH back in
gcloud compute ssh n8n-server --zone=us-central1-a
```

---

### Step 5: Create n8n Directory Structure

```bash
# Create directories
mkdir -p ~/n8n
cd ~/n8n

# Create data directory for n8n
mkdir -p n8n-data
mkdir -p postgres-data
mkdir -p nginx/conf.d
mkdir -p nginx/ssl
```

---

### Step 6: Create docker-compose.yml

```bash
cd ~/n8n
nano docker-compose.yml
```

**Paste this content:**

```yaml
version: '3.8'

services:
  # PostgreSQL Database for n8n
  postgres:
    image: postgres:15-alpine
    container_name: n8n-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    networks:
      - n8n-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U n8n_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # n8n Automation Platform
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      # Database
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n_user
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      
      # n8n Configuration
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_DOMAIN}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://${N8N_DOMAIN}
      - GENERIC_TIMEZONE=${TIMEZONE}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      
      # Performance
      - EXECUTIONS_PROCESS=main
      - EXECUTIONS_MODE=regular
    volumes:
      - ./n8n-data:/home/node/.n8n
    networks:
      - n8n-network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: n8n-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - certbot-webroot:/var/www/certbot
    networks:
      - n8n-network
    depends_on:
      - n8n

  # Certbot for SSL
  certbot:
    image: certbot/certbot
    container_name: n8n-certbot
    volumes:
      - ./nginx/ssl:/etc/letsencrypt
      - certbot-webroot:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    networks:
      - n8n-network

volumes:
  certbot-webroot:
    driver: local

networks:
  n8n-network:
    driver: bridge
```

**Save:** `Ctrl+X`, `Y`, `Enter`

---

### Step 7: Create Environment File

```bash
nano .env
```

**Paste and customize:**

```bash
# PostgreSQL
POSTGRES_PASSWORD=<generate-strong-password>

# n8n Authentication
N8N_USER=admin
N8N_PASSWORD=<generate-strong-password>
N8N_ENCRYPTION_KEY=<generate-32-char-key>

# Domain
N8N_DOMAIN=n8n.trart.uk

# Settings
TIMEZONE=Asia/Dubai
```

**Generate secure values:**

```bash
# PostgreSQL password
openssl rand -base64 32

# n8n encryption key (at least 10 chars, use 32 for security)
openssl rand -hex 16

# n8n password (for login)
openssl rand -base64 24
```

**Copy these values into .env file**

**Save:** `Ctrl+X`, `Y`, `Enter`

---

### Step 8: Create Nginx Configuration

```bash
# Create main nginx.conf
nano nginx/nginx.conf
```

**Paste:**

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    include /etc/nginx/conf.d/*.conf;
}
```

**Save and create n8n config:**

```bash
nano nginx/conf.d/n8n.conf
```

**Paste (temporary HTTP-only for SSL setup):**

```nginx
server {
    listen 80;
    server_name n8n.trart.uk;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://n8n:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

**Save:** `Ctrl+X`, `Y`, `Enter`

---

### Step 9: Configure DNS

**Go to your domain registrar where you manage trart.uk:**

**Add A Record:**
```
Type: A
Name: n8n
Value: <Your GCP IP from Step 2>
TTL: 3600
```

**Test DNS propagation:**

```bash
# Wait 5-30 minutes, then test:
nslookup n8n.trart.uk

# Should show your GCP IP
```

**Don't proceed until DNS is working!**

---

### Step 10: Start n8n

```bash
# Make sure you're in ~/n8n directory
cd ~/n8n

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f n8n
```

**All containers should show "Up" status**

---

### Step 11: Obtain SSL Certificate

```bash
# Request certificate
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d n8n.trart.uk \
  --email your-email@gmail.com \
  --agree-tos \
  --no-eff-email

# Should see: "Successfully received certificate"
```

---

### Step 12: Enable HTTPS

```bash
# Update nginx config with SSL
nano nginx/conf.d/n8n.conf
```

**Replace entire content with:**

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    server_name n8n.trart.uk;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - n8n
server {
    listen 443 ssl http2;
    server_name n8n.trart.uk;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/n8n.trart.uk/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/n8n.trart.uk/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Client Settings
    client_max_body_size 50M;

    # Proxy to n8n
    location / {
        proxy_pass http://n8n:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts for long-running workflows
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    # WebSocket support
    location /rest/push {
        proxy_pass http://n8n:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Save and restart nginx:**

```bash
docker compose restart nginx
```

---

### Step 13: Access n8n

**Open in browser:**
```
https://n8n.trart.uk
```

**Login with:**
- Username: `admin` (or what you set in .env)
- Password: (from N8N_PASSWORD in .env)

**🎉 Your n8n is now running 24/7!**

---

## 📦 Import Your Existing Workflows

### Option 1: Via Web UI (Easiest)

1. Open https://n8n.trart.uk
2. Click "Workflows"
3. Click "Import from File"
4. Select your workflow JSON files
5. Click "Import"

### Option 2: Upload Files First

**From local machine:**

```powershell
# Upload workflows to server
cd C:\n8n-backup\workflows
gcloud compute scp *.json n8n-server:~/ --zone=us-central1-a
```

**Then import in n8n UI**

---

## 🔐 Recreate Credentials

For each credential you documented:

1. Go to "Credentials" in n8n
2. Click "Add Credential"
3. Select credential type
4. **Use exact same name as before**
5. Fill in values (API keys, etc.)
6. Save

---

## 🔧 Connect to Your Material Dashboard

### On Dashboard Server:

Update dashboard's `.env` file with:

```bash
N8N_WEBHOOK_URL=https://n8n.trart.uk/webhook
N8N_BASE_URL=https://n8n.trart.uk
N8N_TO_FLASK_API_KEY=<your-api-key>
```

Restart dashboard to apply changes.

---

## 💾 Backup Strategy

### Manual Backup

```bash
# SSH to n8n server
gcloud compute ssh n8n-server --zone=us-central1-a

# Create backup directory
mkdir -p ~/backups

# Backup database
docker compose exec -T postgres pg_dump -U n8n_user n8n | \
  gzip > ~/backups/n8n_backup_$(date +%Y%m%d).sql.gz

# Backup n8n data
tar -czf ~/backups/n8n_data_$(date +%Y%m%d).tar.gz ~/n8n/n8n-data/
```

### Automated Backup Script

```bash
cat > ~/backup-n8n.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
cd ~/n8n
docker compose exec -T postgres pg_dump -U n8n_user n8n | \
  gzip > $BACKUP_DIR/n8n_db_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup n8n data
tar -czf $BACKUP_DIR/n8n_data_$(date +%Y%m%d_%H%M%S).tar.gz n8n-data/

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $(date)"
EOF

chmod +x ~/backup-n8n.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/YOUR_USERNAME/backup-n8n.sh >> /var/log/n8n-backup.log 2>&1
```

---

## 🎯 Useful Commands

### View Logs

```bash
# All services
docker compose logs -f

# Just n8n
docker compose logs -f n8n

# Just nginx
docker compose logs -f nginx

# Last 50 lines
docker compose logs --tail=50
```

### Restart Services

```bash
# Restart n8n
docker compose restart n8n

# Restart all
docker compose restart

# Stop all
docker compose down

# Start all
docker compose up -d
```

### Update n8n

```bash
cd ~/n8n

# Pull latest image
docker compose pull n8n

# Restart with new image
docker compose up -d n8n
```

---

## 🔧 Maintenance

### Monitor Resources

```bash
# Check disk space
df -h

# Check Docker resource usage
docker stats

# Check n8n container
docker compose ps
```

### Clean Up Docker

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a
```

---

## 💰 Cost Management

### Stop n8n When Not Needed

```bash
# Stop VM (saves money)
gcloud compute instances stop n8n-server --zone=us-central1-a

# Start when needed
gcloud compute instances start n8n-server --zone=us-central1-a
```

### Monitor Costs

- Go to: GCP Console > Billing > Reports
- Set budget alerts at $10, $20, $30/month
- Track spending weekly

---

## 🆘 Troubleshooting

### Can't Access n8n.trart.uk

```bash
# Check DNS
nslookup n8n.trart.uk

# Check containers
docker compose ps

# Check n8n logs
docker compose logs n8n

# Check nginx
docker compose logs nginx

# Test without SSL
curl http://YOUR_GCP_IP:5678
```

### Forgot Password

```bash
# Update in .env file
nano ~/n8n/.env
# Change N8N_PASSWORD

# Restart n8n
docker compose restart n8n
```

### Database Issues

```bash
# Check postgres logs
docker compose logs postgres

# Access database
docker compose exec postgres psql -U n8n_user -d n8n
```

---

## ✅ Post-Deployment Checklist

- [ ] GCP VM created (e2-small)
- [ ] Static IP reserved and attached
- [ ] Docker and Docker Compose installed
- [ ] n8n deployed and running
- [ ] DNS configured (n8n.trart.uk → GCP IP)
- [ ] DNS propagated (nslookup works)
- [ ] SSL certificate obtained
- [ ] HTTPS working (https://n8n.trart.uk)
- [ ] Can login to n8n
- [ ] Workflows imported
- [ ] Credentials recreated
- [ ] Workflows tested
- [ ] Dashboard connected to n8n
- [ ] Backup script created
- [ ] Budget alerts set

---

## 🎉 Success!

Your standalone n8n is now:
- ✅ Running 24/7 on dedicated server
- ✅ Accessible at https://n8n.trart.uk
- ✅ Secured with SSL
- ✅ Using PostgreSQL (production-ready)
- ✅ Auto-starts on server reboot
- ✅ Isolated from other projects

**Monthly Cost:** ~$13/month (FREE for 3 months with GCP trial)

---

**Created:** October 10, 2025  
**Last Updated:** October 10, 2025
