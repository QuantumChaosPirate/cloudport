# CloudPort User Manual

*Your personal cloud. Your data. Your rules.*

This manual covers everything from installing CloudPort to using it day to day. No technical knowledge required.

---

## Table of Contents

1. [Before You Begin](#1-before-you-begin)
2. [Installation](#2-installation)
3. [First Time Setup](#3-first-time-setup)
4. [Logging In](#4-logging-in)
5. [The Dashboard](#5-the-dashboard)
6. [Managing Files](#6-managing-files)
7. [Managing Users](#7-managing-users)
8. [Parental Controls](#8-parental-controls)
9. [Media Server](#9-media-server)
10. [Notes](#10-notes)
11. [Monitoring & Costs](#11-monitoring--costs)
12. [Updating CloudPort](#12-updating-cloudport)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Before You Begin

Before installing CloudPort you will need:

- A **Microsoft Azure account** — [create one free at azure.microsoft.com](https://azure.microsoft.com/free). The free account gives you €200 credit for the first 30 days.
- A **domain name** — a web address for your CloudPort (e.g. `mycloud.example.com`). You can buy one from Namecheap, GoDaddy, or any domain registrar for around €10-15/year.
- A **computer with a terminal** — on Windows, use PowerShell or WSL. On Mac or Linux, use the built-in Terminal.

**Estimated monthly cost after free trial:** €10-20 depending on storage.

**Estimated setup time:** 20-30 minutes.

---

## 2. Installation

### Step 1 — Install the required tools

You need two tools on your computer: the Azure CLI and Terraform.

**On Linux:**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
sudo snap install terraform --classic
```

**On Mac:**
```bash
brew install azure-cli terraform
```

**On Windows:**
- Download [Azure CLI](https://aka.ms/installazurecliwindows)
- Download [Terraform](https://developer.hashicorp.com/terraform/downloads)

---

### Step 2 — Download CloudPort

```bash
git clone https://github.com/QuantumChaosPirate/cloudport.git
cd cloudport
```

---

### Step 3 — Log in to Azure

```bash
az login
```

A browser window will open. Sign in with your Microsoft account.

---

### Step 4 — Find your Azure Subscription ID

```bash
az account show --query id --output tsv
```

Copy the output — you will need it in the next step.

---

### Step 5 — Configure the infrastructure

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Fill in your details:
# CloudPort User Manual

*Your personal cloud. Your data. Your rules.*

This manual covers everything from installing CloudPort to using it day to day. No technical knowledge required.

---

## Table of Contents

1. [Before You Begin](#1-before-you-begin)
2. [Installation](#2-installation)
3. [First Time Setup](#3-first-time-setup)
4. [Logging In](#4-logging-in)
5. [The Dashboard](#5-the-dashboard)
6. [Managing Files](#6-managing-files)
7. [Managing Users](#7-managing-users)
8. [Parental Controls](#8-parental-controls)
9. [Media Server](#9-media-server)
10. [Notes](#10-notes)
11. [Monitoring & Costs](#11-monitoring--costs)
12. [Updating CloudPort](#12-updating-cloudport)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Before You Begin

Before installing CloudPort you will need:

- A **Microsoft Azure account** — [create one free at azure.microsoft.com](https://azure.microsoft.com/free). The free account gives you €200 credit for the first 30 days.
- A **domain name** — a web address for your CloudPort (e.g. `mycloud.example.com`). You can buy one from Namecheap, GoDaddy, or any domain registrar for around €10-15/year.
- A **computer with a terminal** — on Windows, use PowerShell or WSL. On Mac or Linux, use the built-in Terminal.

**Estimated monthly cost after free trial:** €10-20 depending on storage.

**Estimated setup time:** 20-30 minutes.

---

## 2. Installation

### Step 1 — Install the required tools

You need two tools on your computer: the Azure CLI and Terraform.

**On Linux:**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Terraform
sudo snap install terraform --classic
```

**On Mac:**
```bash
brew install azure-cli terraform
```

**On Windows:**
- Download [Azure CLI](https://aka.ms/installazurecliwindows)
- Download [Terraform](https://developer.hashicorp.com/terraform/downloads)

---

### Step 2 — Download CloudPort

```bash
git clone https://github.com/QuantumChaosPirate/cloudport.git
cd cloudport
```

---

### Step 3 — Log in to Azure

```bash
az login
```

A browser window will open. Sign in with your Microsoft account.

---

### Step 4 — Find your Azure Subscription ID

```bash
az account show --query id --output tsv
```

Copy the output — you will need it in the next step.

---

### Step 5 — Configure the infrastructure

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Fill in your details:
subscription_id = "paste-your-subscription-id-here"
location = "westeurope"
project_name = "cloudport"
environment = "prod"
vm_size = "Standard_B1s"

Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).

---

### Step 6 — Create your Azure infrastructure

```bash
terraform init
terraform apply
```

Type `yes` when prompted. This takes 2-3 minutes.

When complete, note the `public_ip_address` from the output — this is your server's address.

---

### Step 7 — Point your domain to your server

In your domain registrar's DNS settings, create an A record:

| Field | Value |
|---|---|
| Type | A |
| Name | @ (or your subdomain) |
| Value | YOUR_SERVER_IP |
| TTL | 3600 |

DNS changes take 5-30 minutes to take effect.

---

### Step 8 — Get your Azure Storage connection string

```bash
az storage account show-connection-string \
  --name cloudportdevsa \
  --resource-group cloudport-dev-rg \
  --output tsv
```

Copy the entire output — you will need it during the setup wizard.

---

### Step 9 — Bootstrap your server

SSH into your server:

```bash
ssh -i ~/.ssh/id_rsa_cloudport cloudport@YOUR_SERVER_IP
```

Run the bootstrap script:

```bash
sudo bash -c "curl -fsSL https://raw.githubusercontent.com/QuantumChaosPirate/cloudport/main/scripts/bootstrap.sh | bash"
```

When prompted, edit the configuration file:

```bash
nano /cloudport/.env
```

Fill in all the values — your Azure connection string, domain name, and passwords. Save and exit, then run:

```bash
cd /cloudport && sudo docker compose up -d
```

---

### Step 10 — Run database migrations

```bash
sudo docker compose run --rm cloudport-api alembic upgrade head
```

---

### Step 11 — Complete setup in your browser

Visit `https://yourdomain.com` in your browser. The CloudPort setup wizard will appear.

---

## 3. First Time Setup

The setup wizard guides you through six steps:

**Step 1 — Welcome**
Read the overview of what CloudPort will set up for you. Click **Get Started**.

**Step 2 — Azure Storage**
Enter your Azure Storage Account Name and Connection String from Step 8 above. CloudPort uses this to store your files securely.

**Step 3 — Domain**
Enter your domain name and email address. CloudPort will automatically set up a secure HTTPS connection.

**Step 4 — Storage Plan**
Choose how much storage you want. The price shown is your estimated monthly Azure cost for storage.

| Plan | Storage | Estimated Cost |
|---|---|---|
| Small | 100 GB | ~€2/month |
| Medium | 500 GB | ~€10/month |
| Large | 1 TB | ~€20/month |

**Step 5 — Owner Account**
Create your Owner account. This is the master account — keep these credentials safe. You also set your Jellyfin media server password here.

**Step 6 — Done**
CloudPort is ready. Click **Go to Dashboard**.

---

## 4. Logging In

Visit your CloudPort domain in any browser. You will see the login screen.

Enter your **username** and **password** from the setup wizard and click **Sign In**.

You will be taken to the dashboard automatically.

**Forgotten your password?** Contact your CloudPort Owner to reset it.

---

## 5. The Dashboard

The dashboard has four sections accessible from the left sidebar:

| Section | Who can see it | What it shows |
|---|---|---|
| **Home** | Everyone | Storage usage, service links, system health |
| **Files** | Everyone | Your files and files shared with you |
| **Users** | Owner and Admin | All users, their quotas and roles |
| **Approvals** | Owner and Admin | Files from child accounts waiting for approval |

At the bottom of the sidebar you can see your username and role, and sign out.

---

## 6. Managing Files

### Uploading a file

1. Click **Files** in the sidebar
2. Click **Upload File**
3. Select a file from your computer
4. Wait for the upload and malware scan to complete
5. The file appears in your file list once approved

Every file is automatically scanned for malware before it is stored. This happens in the background and takes a few seconds.

### Downloading a file

Click **Download** next to any file. A secure download link is generated automatically.

### Sharing a file

1. Click **Share** next to a file
2. Enter the User ID of the person you want to share with
3. Choose their permission level — Read only or Read and write
4. Click **Share**

To find a user's ID, an Owner or Admin can check the Users section.

### Deleting a file

Click **Delete** next to a file and confirm. Deleted files cannot be recovered.

---

## 7. Managing Users

*Owner and Admin only.*

### Inviting a new user

1. Ask the new user to visit your CloudPort domain
2. They register their own account via the login page
3. They are automatically assigned the **User** role
4. An Owner can promote them to Admin if needed

### User roles explained

| Role | What they can do |
|---|---|
| **Owner** | Full control — billing, infrastructure, all settings. Only one per instance. |
| **Admin** | Manage users, approve uploads, configure sharing. Cannot access billing. |
| **User** | Access their own files and shared files. |
| **Child** | Restricted access. Uploads may require Admin approval. |

### Changing a user's storage quota

1. Go to **Users** in the sidebar
2. Find the user
3. Their current usage is shown — contact them before reducing their quota

### Deactivating an account

Click **Deactivate** next to a user to suspend their access. Their files are preserved. Click **Activate** to restore access.

---

## 8. Parental Controls

Child accounts have additional restrictions for safety.

### Setting up a child account

1. Ask your child to create an account on your CloudPort
2. Go to **Users** → find their account
3. Click **Enable Approval** to require your approval before any of their uploads are processed

### Approving uploads

When a child uploads a file:
1. You receive a notification (visible in the **Approvals** section)
2. Go to **Approvals** in the sidebar
3. Review the file details
4. Click **Approve** to allow it or **Reject** to decline it

Rejected files are permanently deleted.

---

## 9. Media Server

CloudPort includes Jellyfin — an open source media server for streaming your movies, TV shows, and music.

### Accessing Jellyfin

From the dashboard Home page, click **Jellyfin** under Services. It opens in a new tab.

Log in with the Jellyfin password you set during the setup wizard.

### Adding media

Media files need to be placed in the correct folders on your server:

| Media type | Folder |
|---|---|
| Movies | `/media/movies` |
| TV Shows | `/media/tvshows` |
| Music | `/media/music` |

You can upload files to these folders via SSH or by adding them through the Jellyfin interface directly.

### Streaming on other devices

Jellyfin has apps for:
- iOS and Android
- Smart TVs (Samsung, LG)
- Roku, Fire TV, Apple TV
- Web browser

Download the Jellyfin app and enter your CloudPort domain when asked for a server address.

---

## 10. Notes

CloudPort includes Outline — an open source collaborative notes and documents application similar to Notion.

### Accessing Outline

From the dashboard Home page, click **Outline** under Services.

You can create documents, organise them into collections, and share them with other CloudPort users.

---

## 11. Monitoring & Costs

### Accessing the monitoring dashboard

From the dashboard Home page, click **Grafana** under Services. *Visible to Owner and Admin only.*

Log in with your Grafana credentials set during installation.

The dashboard shows:
- Total requests to your CloudPort
- API response times
- Error rates
- Memory and CPU usage

### Managing your storage costs

Your storage usage is shown on the dashboard Home page. The bar turns **orange** when you reach 80% and **red** at 95%.

**To expand your storage:**
1. Go to the Azure Portal
2. Navigate to your Storage Account
3. Review the current usage and costs
4. Acknowledge the new monthly cost before confirming

**To reduce costs:**
- Delete files you no longer need
- Reduce user storage quotas from the Users section
- Stop the VM when not in use (Azure Portal → Virtual Machines → Stop)

### Setting a spending alert

In the Azure Portal:
1. Go to **Cost Management** → **Budgets**
2. Create a budget of your expected monthly spend
3. Set alerts at 80% and 100%
4. Azure will email you before you overspend

---

## 12. Updating CloudPort

To update CloudPort to the latest version, SSH into your server:

```bash
ssh -i ~/.ssh/id_rsa_cloudport cloudport@YOUR_SERVER_IP
cd /cloudport
git pull origin main
sudo docker compose build cloudport-api
sudo docker compose up -d
sudo docker compose run --rm cloudport-api alembic upgrade head
```

Updates are applied automatically if you have the GitHub Actions CI/CD pipeline configured.

---

## 13. Troubleshooting

### CloudPort is not loading

Check if all services are running:
```bash
sudo docker compose ps
```

Restart all services:
```bash
sudo docker compose restart
```

### I forgot my password

An Owner or Admin can reset passwords directly in the database. Contact your CloudPort Owner.

### A file upload failed

- Check your storage quota on the dashboard Home page
- If you are a child account, your upload may be pending Admin approval — check with your Admin
- The file may have failed the malware scan — try a different file

### Jellyfin is not loading

```bash
sudo docker compose logs cloudport-jellyfin
```

### The dashboard shows the database as offline

```bash
sudo docker compose logs db
sudo docker compose restart db
```

### SSL certificate issues

```bash
sudo docker compose logs cloudport-certbot
```

### General logs

```bash
# API logs
sudo docker compose logs cloudport-api

# All service logs
sudo docker compose logs
```

---

## Getting Help

- **GitHub Issues:** [github.com/QuantumChaosPirate/cloudport/issues](https://github.com/QuantumChaosPirate/cloudport/issues)
- **Documentation:** [github.com/QuantumChaosPirate/cloudport/docs](https://github.com/QuantumChaosPirate/cloudport/docs)

---

*CloudPort is open source software released under the MIT License.*
*Built by Daniel Buhagiar.*
