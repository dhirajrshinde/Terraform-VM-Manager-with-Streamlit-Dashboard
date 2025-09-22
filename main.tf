terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">=3.5.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

locals {
  common_tags = merge({
    Project = "WindowsVM-Terraform"
  }, var.tags)
}

module "resource_group" {
  source = "./modules/resource_group"
  name   = var.resource_group_name
}

module "network" {
  source      = "./modules/network"
  rg_name     = module.resource_group.name
  vnet_name   = var.vnet_name
  subnet_name = var.subnet_name
}

module "compute" {
  source         = "./modules/compute"
  rg_name        = module.resource_group.name
  location       = module.resource_group.location
  vm_name        = var.vm_name
  vm_size        = var.vm_size
  admin_username = var.admin_username
  admin_password = var.admin_password
  os_disk_type   = var.os_disk_type
  tags           = local.common_tags
}

