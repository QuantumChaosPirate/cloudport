variable "subscription_id" {
  description = "Your Azure subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region to deploy into"
  type        = string
  default     = "westeurope"
}

variable "project_name" {
  description = "Used to prefix all resource names"
  type        = string
  default     = "cloudport"
}

variable "environment" {
  description = "dev, staging, or prod"
  type        = string
  default     = "dev"
}

variable "vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for the VM"
  type        = string
  default     = "cloudport"
}
