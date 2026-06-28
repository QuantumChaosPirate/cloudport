output "public_ip_address" {
  description = "The public IP address of the CloudPort VM"
  value       = azurerm_public_ip.main.ip_address
}

output "resource_group_name" {
  description = "The name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "storage_account_name" {
  description = "The name of the storage account"
  value       = azurerm_storage_account.main.name
}

output "vm_name" {
  description = "The name of the virtual machine"
  value       = azurerm_linux_virtual_machine.main.name
}
