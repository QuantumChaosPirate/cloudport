# CloudPort API Reference

The CloudPort API is built with FastAPI and provides automatic interactive documentation at `/docs` on your CloudPort instance.

Base URL: `https://yourdomain.com`

---

## Authentication

CloudPort uses JWT Bearer token authentication.

**Login:**
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=yourname&password=yourpassword
**Use the token:**
Authorization: Bearer YOUR_TOKEN
Tokens expire after 30 minutes.

---

## Endpoints

### Auth
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and get token | No |

### Users
| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/users/me` | Get current user | Any |
| GET | `/users/` | List all users | Admin, Owner |
| PATCH | `/users/{id}/quota` | Update storage quota | Owner |
| PATCH | `/users/{id}/role` | Update user role | Owner |
| PATCH | `/users/{id}/upload-approval` | Toggle upload approval | Admin, Owner |
| PATCH | `/users/{id}/active` | Deactivate/reactivate account | Admin, Owner |

### Storage
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/storage/presigned-upload` | Get upload URL | Yes |
| GET | `/storage/presigned-download/{key}` | Get download URL | Yes |
| POST | `/storage/scan/{key}` | Scan and promote file | Yes |

### Files
| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| GET | `/files/` | List own files | Any |
| GET | `/files/shared` | List shared files | Any |
| GET | `/files/pending` | List pending approvals | Admin, Owner |
| PATCH | `/files/{id}/approve` | Approve or reject file | Admin, Owner |
| POST | `/files/{id}/share` | Share file with user | Any |
| DELETE | `/files/{id}` | Delete file | Any (own files) |

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/` | API health check |
| GET | `/metrics` | Prometheus metrics |

---

## Interactive Documentation

Visit `/docs` on your CloudPort instance for an interactive API explorer where you can test all endpoints directly in the browser.
