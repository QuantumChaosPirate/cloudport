<div align="center">

# CloudPort

**Self-hostable personal cloud platform with simple setup, use and management**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![Terraform](https://img.shields.io/badge/Terraform-1.6+-purple)](https://terraform.io)

*Your cloud. Your data. Your rules.*

</div>

---

## What is CloudPort?

CloudPort is an open-source, self-hostable personal cloud platform that creates a home-server with features of multiple services (such as: Google Drive, Plex, Notion, etc.) — hosted on your own Azure infrastructure, at a predictable monthly cost.

No forced subscriptions, data sharing or surprise bills

---

## Features

- **Cloud Storage** — Secure file storage with per-user quotas and storage management
- **Media Streaming** — Jellyfin media server for movies, TV shows, and music
- **Notes** — Outline-powered collaborative notes and documents
- **Malware Scanning** — ClamAV scans every upload before it reaches your storage
- **Family Friendly** — Multi-user with parental controls and upload approval gates
- **Encrypted** — HTTPS everywhere, storage encrypted at rest, no plain text credentials
- **Cost Controls** — Spending alerts and storage limits so you're never surprised
- **Easy Setup** — Browser-based setup wizard, no terminal required after initial deployment

---

## Architecture

CloudPort runs on a single Azure VM with all services containerised via Docker:

Internet → Nginx (reverse proxy, TLS) → CloudPort API (FastAPI)
→ Jellyfin (media)
→ Outline (notes)
→ Grafana (monitoring)


Infrastructure is provisioned via Terraform — reproducible, version controlled, and portable.

---

## Quick Start

### Prerequisites
- An Azure account
- A domain name
- A Linux terminal (only needed once)

### 1. Provision Infrastructure

```bash
git clone https://github.com/QuantumChaosPirate/cloudport.git
cd cloudport/infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your Azure subscription ID
terraform init
terraform apply
```

### 2. Bootstrap the VM

SSH into your new VM and run:

```bash
curl -fsSL https://raw.githubusercontent.com/QuantumChaosPirate/cloudport/main/scripts/bootstrap.sh | bash
```

### 3. Complete Setup

Visit `https://yourdomain.com` in your browser and follow the setup wizard.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud | Microsoft Azure |
| Infrastructure as Code | Terraform |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL + SQLAlchemy |
| Storage | Azure Blob Storage |
| Reverse Proxy | Nginx |
| TLS | Let's Encrypt + Certbot |
| Media Server | Jellyfin |
| Notes | Outline |
| Malware Scanning | ClamAV |
| Monitoring | Prometheus + Grafana |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## User Roles

| Role | Description |
|---|---|
| **Owner** | Full system access, billing control, storage management |
| **Admin** | User management, content moderation, parental controls |
| **User** | Standard access to own storage and shared resources |
| **Child** | Restricted access, upload approval required, elevated backups |

---

## Cost

CloudPort is designed to run comfortably for 4-6 users at **€10-20/month** on Azure, depending on storage usage. The setup wizard shows live cost estimates before you commit to a storage plan.

---

## Documentation

- [Setup Guide](docs/setup.md) — Step-by-step installation with screenshots
- [Architecture](docs/architecture.md) — Technical overview and design decisions
- [API Reference](docs/api.md) — FastAPI endpoint documentation

---

## Contributing

CloudPort is open source and welcomes contributions. Please read the setup guide to get a local development environment running.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built by <a href="https://github.com/QuantumChaosPirate">Daniel Buhagiar</a>
</div>
