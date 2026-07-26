# CloudPort Architecture

## Overview

CloudPort runs entirely on a single Azure VM with all services containerised via Docker Compose. Nginx acts as the central reverse proxy — all incoming traffic hits Nginx first, which routes to the correct service based on the URL path.

---

## Infrastructure

Provisioned via Terraform:

- **Resource Group** — contains all Azure resources
- **Virtual Network + Subnet** — private network for the VM
- **Public IP** — static IP address for the domain
- **Network Security Group** — firewall allowing only ports 22, 80, 443
- **VM** — Debian Linux, B-series budget tier
- **Storage Account** — Azure Blob Storage with quarantine and production containers

---

## Services

| Service | Port | Purpose |
|---|---|---|
| Nginx | 80, 443 | Reverse proxy, TLS termination |
| CloudPort API | 8000 (internal) | FastAPI backend |
| PostgreSQL | 5432 (internal) | Primary database |
| Jellyfin | 8096 (internal) | Media streaming |
| ClamAV | Internal | Malware scanning |
| Outline | 3000 (internal) | Notes application |
| Redis | 6379 (internal) | Outline caching |
| Prometheus | 9090 (internal) | Metrics collection |
| Grafana | 3000 (internal) | Monitoring dashboard |
| Certbot | Sidecar | SSL certificate renewal |

---

## File Upload Flow
1. Client requests presigned URL → POST /storage/presigned-upload
2. Client uploads directly to Azure Blob Storage (quarantine container)
3. Client triggers scan → POST /storage/scan/{object_key}
4. Backend checks storage quota
5. Backend checks upload approval (child accounts)
6. ClamAV scans the file
7. Clean → promoted to production container
8. Infected → deleted from quarantine, user notified

---

## Security

- TLS everywhere — Let's Encrypt certificates, auto-renewed
- Storage encrypted at rest — Azure Blob Storage default encryption
- Passwords hashed with bcrypt — never stored in plain text
- JWT authentication — 30 minute access tokens, refresh token flow
- Role-based access control — Owner, Admin, User, Child
- Malware scanning — every upload scanned before reaching production
- Fail-safe scanning — if ClamAV is unavailable, uploads are rejected

---

## Database Schema

- **users** — accounts, roles, storage quotas, parental control flags
- **files** — file metadata, ownership, approval status
- **shared_access** — file sharing permissions between users
- **alembic_version** — migration tracking

---

## Design Decisions

**Why Azure?** Predictable flat-rate billing suitable for non-technical users.

**Why Terraform?** Cloud-agnostic IaC means the project could be ported to AWS or GCP with minimal changes.

**Why FastAPI?** Async Python, automatic OpenAPI documentation, excellent performance for an I/O-heavy application.

**Why presigned URLs?** Files never pass through the backend server — direct client-to-storage uploads keep bandwidth costs low and reduce server load.

**Why quarantine/production split?** Every file must pass malware scanning before reaching production. The split enforces this at the infrastructure level, not just the application level.
