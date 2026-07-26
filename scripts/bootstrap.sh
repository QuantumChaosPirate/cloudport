#!/bin/bash
# CloudPort Bootstrap Script
# Runs once on first VM boot to set up the entire CloudPort platform

set -e #If anything fails, script is ended immediately to prevent broken Cloudport install

echo "========================================="
echo "  CloudPort Bootstrap"
echo "========================================="

# ── Step 1: System Update ─────────────────────────────────────────────────────
#Updates all system packages before installing anything [-qq, it runs in quiet mode, minimal output]
#[-y, auto-confirms all prompts made, makes scripts run autonomously, without user interaction]
echo "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# ── Step 2: Install Docker ────────────────────────────────────────────────────
#Downloads and runs Docker's official install script, makes it start automatically start every VM reboot
#it is then started immediately
echo "Installing Docker..."
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# ── Step 3: Install Docker Compose ───────────────────────────────────────────
#Installs Docker Compose as a Docker plugin, enabling the docker compose command
echo "Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# ── Step 4: Clone CloudPort ───────────────────────────────────────────────────
#Downloads the entire project from Github into it's own directory /cloudport on the VM.
#Bootstrap script pulls everything from Github
echo "Cloning CloudPort..."
git clone https://github.com/QuantumChaosPirate/cloudport.git /cloudport
cd /cloudport

# ── Step 5: Create environment file ──────────────────────────────────────────
#Checks if a .env file exists. If it doesn't, it copies the example file and stops
#This makes the user requre to fill in their azure credentials, domain and passwords before continuing
#Only manual step after running the bootstrap script
echo "Setting up environment..."
if [ ! -f /cloudport/.env ]; then
    cp /cloudport/.env.example /cloudport/.env
    echo "Please edit /cloudport/.env with your settings before continuing"
    exit 1
fi

# ── Step 6: Run database migrations ──────────────────────────────────────────
#Runs Alembic migrations inside the API container
#creates all databases and then removes temp container after command finishes
echo "Running database migrations..."
docker compose run --rm cloudport-api alembic upgrade head

# ── Step 7: Start all services ────────────────────────────────────────────────
#Starts every service defines in the docker compose file in detatched mode
#All containers start in the correct order based on their depends_on configuration
echo "Starting CloudPort services..."
docker compose up -d

# ── Step 8: Issue SSL certificate ────────────────────────────────────────────
echo "Issuing SSL certificate..."
DOMAIN=$(grep DOMAIN /cloudport/.env | cut -d= -f2)
EMAIL=$(grep CERTBOT_EMAIL /cloudport/.env | cut -d= -f2)

#Requests an SSL certificate from Let's Encrypt from the domain of the user 
#Uses the webroot  method, Certbotplaces a verification file in /var/www/certbot
#and Let's Encrypt verifies the domain by fetching it over HTTP
#After this, Nginx is reloaded to start serving HTTPS.
docker compose run --rm certbot certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
