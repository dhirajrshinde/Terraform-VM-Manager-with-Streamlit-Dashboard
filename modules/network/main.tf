variable "rg_name" {
  type = string
}

variable "vnet_name" {
  type = string
}

variable "subnet_name" {
  type = string
}

data "azurerm_virtual_network" "existing" {
  name                = var.vnet_name
  resource_group_name = var.rg_name
}

data "azurerm_subnet" "existing" {
  name                 = var.subnet_name
  virtual_network_name = var.vnet_name
  resource_group_name  = var.rg_name
}

output "vnet_name" {
  value = data.azurerm_virtual_network.existing.name
}

output "subnet_name" {
  value = data.azurerm_subnet.existing.id
}
