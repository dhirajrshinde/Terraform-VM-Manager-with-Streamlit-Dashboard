variable "rg_name" {
  type = string
}

variable "location" {
  type = string
}

variable "vm_name" {
  type = string
}

variable "vm_size" {
  type = string
}

variable "subnet_id" {
  type    = string
  default = "/subscriptions/15cb3ee3-c143-4893-83fd-09a6efa7b01f/resourceGroups/rg-cirrus-standard-01/providers/Microsoft.Network/virtualNetworks/vNet-cs-graduates-2025-57362353-cirrus-standard-01/subnets/sNet-cirrus-std-02"
}

variable "admin_username" {
  type = string
}

variable "admin_password" {
  type      = string
  sensitive = true
}

variable "os_disk_type" {
  type = string
}

variable "tags" {
  type = map(string)
}

resource "azurerm_network_interface" "nic" {
  name                = "${var.vm_name}-nic"
  location            = var.location
  resource_group_name = var.rg_name
  tags                = var.tags

  ip_configuration {
    name                          = "ipconfig1"
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = var.subnet_id
  }
}

resource "azurerm_windows_virtual_machine" "vm" {
  name                = var.vm_name
  resource_group_name = var.rg_name
  location            = var.location
  size                = var.vm_size
  admin_username      = var.admin_username
  admin_password      = var.admin_password
  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]


  os_disk {
    caching              = "ReadWrite"
    storage_account_type = var.os_disk_type
  }

  source_image_id = "/subscriptions/92da1ef1-5469-4659-88df-e91ab8b5c0e0/resourceGroups/shared-images-rg/providers/Microsoft.Compute/galleries/amdocs_os_images/images/Windows2022/versions/1.0.052023"

  enable_automatic_updates = true
  patch_mode               = "AutomaticByOS"

  tags = var.tags
}

output "private_ip" {
  value = azurerm_network_interface.nic.private_ip_address
}


