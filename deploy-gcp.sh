#!/bin/bash

# 🌐 GCP Deployment Script for PKP Material Dashboard
# This script automates the deployment on Google Cloud Platform

set -e

echo "🌐 PKP Material Dashboard - GCP Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found${NC}"
    echo ""
    echo "Please install Google Cloud SDK:"
    echo "  https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "Or use the GCP Console deployment method."
    exit 1
fi

echo -e "${GREEN}✅ gcloud CLI detected${NC}"
echo ""

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with Google Cloud${NC}"
    echo "Running authentication..."
    gcloud auth login
fi

ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
echo -e "${GREEN}✅ Authenticated as: $ACCOUNT${NC}"
echo ""

# Prompt for project configuration
echo -e "${BLUE}📋 GCP Project Configuration${NC}"
echo ""

read -p "Enter GCP Project ID (or press Enter to create new): " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo ""
    read -p "Enter new project name (e.g., pkp-dashboard): " PROJECT_NAME
    
    # Create new project
    PROJECT_ID="${PROJECT_NAME}-$(openssl rand -hex 4)"
    echo "Creating project: $PROJECT_ID"
    
    gcloud projects create $PROJECT_ID --name="$PROJECT_NAME"
    
    echo -e "${GREEN}✅ Project created${NC}"
fi

# Set active project
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Active project: $PROJECT_ID${NC}"
echo ""

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# VM Configuration
echo -e "${BLUE}🖥️  VM Instance Configuration${NC}"
echo ""

read -p "Enter VM name [pkp-dashboard-vm]: " VM_NAME
VM_NAME=${VM_NAME:-pkp-dashboard-vm}

echo ""
echo "Select machine type:"
echo "1) e2-small (2 vCPU, 2GB RAM) - ~$13/month"
echo "2) e2-medium (2 vCPU, 4GB RAM) - ~$25/month [RECOMMENDED]"
echo "3) e2-standard-2 (2 vCPU, 8GB RAM) - ~$50/month"
read -p "Enter choice [1-3]: " MACHINE_CHOICE

case $MACHINE_CHOICE in
    1) MACHINE_TYPE="e2-small" ;;
    2) MACHINE_TYPE="e2-medium" ;;
    3) MACHINE_TYPE="e2-standard-2" ;;
    *) MACHINE_TYPE="e2-medium" ;;
esac

echo ""
echo "Select region (closest to your location):"
echo "1) us-central1 (Iowa, USA)"
echo "2) asia-south1 (Mumbai, India) [RECOMMENDED for UAE]"
echo "3) europe-west1 (Belgium)"
echo "4) asia-southeast1 (Singapore)"
read -p "Enter choice [1-4]: " REGION_CHOICE

case $REGION_CHOICE in
    1) REGION="us-central1"; ZONE="us-central1-a" ;;
    2) REGION="asia-south1"; ZONE="asia-south1-a" ;;
    3) REGION="europe-west1"; ZONE="europe-west1-b" ;;
    4) REGION="asia-southeast1"; ZONE="asia-southeast1-a" ;;
    *) REGION="asia-south1"; ZONE="asia-south1-a" ;;
esac

read -p "Enter boot disk size in GB [30]: " DISK_SIZE
DISK_SIZE=${DISK_SIZE:-30}

echo ""
echo -e "${YELLOW}📋 Configuration Summary:${NC}"
echo "  Project: $PROJECT_ID"
echo "  VM Name: $VM_NAME"
echo "  Machine: $MACHINE_TYPE"
echo "  Region: $REGION"
echo "  Zone: $ZONE"
echo "  Disk: ${DISK_SIZE}GB"
echo ""

read -p "Proceed with VM creation? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create VM instance
echo ""
echo "🚀 Creating VM instance..."

gcloud compute instances create $VM_NAME \
  --project=$PROJECT_ID \
  --zone=$ZONE \
  --machine-type=$MACHINE_TYPE \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=${DISK_SIZE}GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server \
  --metadata=startup-script='#!/bin/bash
apt-get update
apt-get install -y docker.io git
systemctl enable docker
systemctl start docker
usermod -aG docker $(who am i | awk "{print \$1}")'

echo -e "${GREEN}✅ VM instance created${NC}"
echo ""

# Create firewall rules
echo "🔥 Configuring firewall rules..."

gcloud compute firewall-rules create allow-http \
  --project=$PROJECT_ID \
  --allow=tcp:80 \
  --target-tags=http-server \
  --description="Allow HTTP traffic" \
  --direction=INGRESS 2>/dev/null || echo "  (HTTP rule already exists)"

gcloud compute firewall-rules create allow-https \
  --project=$PROJECT_ID \
  --allow=tcp:443 \
  --target-tags=https-server \
  --description="Allow HTTPS traffic" \
  --direction=INGRESS 2>/dev/null || echo "  (HTTPS rule already exists)"

echo -e "${GREEN}✅ Firewall rules configured${NC}"
echo ""

# Reserve static IP
echo "📌 Reserving static IP address..."

gcloud compute addresses create ${VM_NAME}-ip \
  --project=$PROJECT_ID \
  --region=$REGION 2>/dev/null || echo "  (IP already reserved)"

EXTERNAL_IP=$(gcloud compute addresses describe ${VM_NAME}-ip --region=$REGION --format="value(address)")

echo -e "${GREEN}✅ Static IP reserved: $EXTERNAL_IP${NC}"
echo ""

# Attach static IP to VM
echo "🔗 Attaching static IP to VM..."

gcloud compute instances delete-access-config $VM_NAME \
  --project=$PROJECT_ID \
  --zone=$ZONE \
  --access-config-name="External NAT" 2>/dev/null || true

gcloud compute instances add-access-config $VM_NAME \
  --project=$PROJECT_ID \
  --zone=$ZONE \
  --access-config-name="External NAT" \
  --address=$EXTERNAL_IP

echo -e "${GREEN}✅ Static IP attached${NC}"
echo ""

# Wait for VM to be ready
echo "⏳ Waiting for VM to be ready..."
sleep 30

# Instructions for next steps
echo ""
echo "=========================================="
echo -e "${GREEN}✅ GCP VM Setup Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1. SSH into your VM:"
echo "   ${YELLOW}gcloud compute ssh $VM_NAME --zone=$ZONE${NC}"
echo ""
echo "2. Clone repository and deploy:"
echo "   ${YELLOW}git clone https://github.com/pranavkithkin/Material-schedules.git${NC}"
echo "   ${YELLOW}cd Material-schedules${NC}"
echo "   ${YELLOW}chmod +x deploy.sh setup-ssl.sh${NC}"
echo "   ${YELLOW}./deploy.sh${NC}"
echo ""
echo "3. Configure DNS records with your domain registrar:"
echo "   ${YELLOW}A    dashboard.yourdomain.com    $EXTERNAL_IP${NC}"
echo "   ${YELLOW}A    n8n.yourdomain.com          $EXTERNAL_IP${NC}"
echo ""
echo "4. After DNS propagation, run SSL setup:"
echo "   ${YELLOW}./setup-ssl.sh${NC}"
echo ""
echo -e "${BLUE}📊 VM Information:${NC}"
echo "  External IP: ${GREEN}$EXTERNAL_IP${NC}"
echo "  Internal IP: $(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].networkIP)')"
echo "  Machine Type: $MACHINE_TYPE"
echo "  Zone: $ZONE"
echo ""
echo -e "${BLUE}💡 Useful Commands:${NC}"
echo "  View VM status: ${YELLOW}gcloud compute instances list${NC}"
echo "  SSH to VM: ${YELLOW}gcloud compute ssh $VM_NAME --zone=$ZONE${NC}"
echo "  Stop VM: ${YELLOW}gcloud compute instances stop $VM_NAME --zone=$ZONE${NC}"
echo "  Start VM: ${YELLOW}gcloud compute instances start $VM_NAME --zone=$ZONE${NC}"
echo "  View costs: ${YELLOW}https://console.cloud.google.com/billing${NC}"
echo ""
echo -e "${GREEN}🎉 Your VM is ready for deployment!${NC}"
echo ""

# Optionally SSH into VM
read -p "SSH into VM now? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    gcloud compute ssh $VM_NAME --zone=$ZONE
fi
