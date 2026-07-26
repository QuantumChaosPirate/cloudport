# CloudPort Setup Guide

This guide walks you through deploying CloudPort on your own Azure account.

---

## Prerequisites

Before you begin you will need:

- A Microsoft Azure account — [create one free](https://azure.microsoft.com/free)
- A domain name — purchased from any registrar (Namecheap, GoDaddy, etc.)
- A computer with a terminal (Linux, Mac, or Windows with WSL)

**Estimated time:** 15-20 minutes

**Estimated monthly cost:** €10-20 depending on storage plan

---

## Step 1 — Install Required Tools

Install Terraform and Azure CLI on your local machine:

**Linux/Mac:**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
sudo snap install terraform --classic
```

**Windows:**
Download and install from:
- [Azure CLI](https://aka.ms/installazurecliwindows)
- [Terraform](https://developer.hashicorp.com/terraform/downloads)

---

## Step 2 — Clone CloudPort

```bash
git clone https://github.com/QuantumChaosPirate/cloudport.git
cd cloudport
```

---

## Step 3 — Configure Azure

Login to your Azure account:

```bash
az login
```

A browser window will open — sign in with your Azure account.

---

## Step 4 — Provision Infrastructure

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
```

Open `terraform.tfvars` and fill in your details:

```hcl
subscription_id = "your-azure-subscription-id"
location        = "westeurope"
project_name    = "cloudport"
environment     = "prod"
vm_size         = "Standard_B1s"
```

To find your subscription ID:
```bash
az account show --query id --output tsv
```

Then run:
```bash
terraform init
terraform apply
```

Type `yes` when prompted. This takes 2-3 minutes.

When complete, note the `public_ip_address` from the output — you'll need it in the next step.

---

## Step 5 — Point Your

Type: A
Name: @ (or your subdomain)
Value: YOUR_VM_IP_ADDRESS
TTL: 3600

DNS propagation takes 5-30 minutes.

---

## Step 6 — Bootstrap the VM

SSH into your VM:

```bash
ssh -i ~/.ssh/id_rsa_cloudport cloudport@YOUR_VM_IP
```

Run the bootstrap script:

```bash
curl -fsSL https://raw.githubusercontent.com/QuantumChaosPirate/cloudport/main/scripts/bootstrap.sh | bash
```

When prompted, edit the `.env` file with your settings:

```bash
nano /cloudport/.env
```

Fill in all the values — your Azure storage connection string, domain name, and passwords.

---

## Step 7 — Complete Setup in Browser

Visit `https://yourdomain.com` in your browser.

The CloudPort setup wizard will guide you through:
1. Confirming your domain and SSL certificate
2. Selecting your storage plan
3. Creating your Owner account
4. Configuring Jellyfin

The wizard takes about 5 minutes.

---

## Accessing Your Services

Once setup is complete:

| Service | URL |
|---|---|
| CloudPort | `https://yourdomain.com` |
| Media Server | `https://yourdomain.com/media` |
| Notes | `https://yourdomain.com/notes` |
| Monitoring | `https://yourdomain.com/monitoring` |

---

## Cost Management

To avoid unexpected bills:

1. Set a budget alert in the Azure Portal — Cost Management → Budgets
2. CloudPort will warn you when storage usage approaches your limit
3. To pause CloudPort, deallocate the VM in the Azure Portal — you only pay for storage while it's stopped

---

## Updating CloudPort

To update to the latest version:

```bash
ssh -i ~/.ssh/id_rsa_cloudport cloudport@YOUR_VM_IP
cd /cloudport
git pull origin main
docker compose build
docker compose up -d
```

Or simply push to your own fork and let the CI/CD pipeline handle it automatically.

---

## Troubleshooting

**Wizard not loading:**
```bash
docker compose logs cloudport-api
```

**SSL certificate issues:**
```bash
docker compose logs certbot
```

**Database issues:**
```bash
docker compose logs db
```

**Restart all services:**
```bash
docker compose restart
```
