variable "name" {
  type = string
}

data "azurerm_resource_group" "existing" {
  name = var.name
}

output "name" {
  value = data.azurerm_resource_group.existing.name
}

output "location" {
  value = data.azurerm_resource_group.existing.location
}
