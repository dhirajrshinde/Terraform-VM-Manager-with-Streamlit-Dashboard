# Terraform VM Manager with Streamlit

This project provides an interactive web-based dashboard built with Streamlit to manage Azure virtual machines using Terraform. It allows users to:

- Create a VM using dynamic Terraform variables
- View live Terraform output logs
- Destroy an existing VM
- Track all actions in a historical log

## Features

- Modify and apply Terraform variables through a user-friendly UI
- Run `terraform init`, `plan`, and `apply` directly from the dashboard
- View detailed output of Terraform commands
- Destroy infrastructure with a single click
- Automatically logs VM creation and deletion in a CSV file

## Technologies Used

- [Streamlit](https://streamlit.io/)
- [Terraform](https://www.terraform.io/)
- Azure (VMs, VNet, Subnet, etc.)

## Prerequisites

- Python 3.8 or later
- Terraform installed and accessible in PATH
- Azure CLI installed and authenticated
- Terraform configuration files present in the working directory, including `main.tf`, `variables.tf`, and `terraform.tfvars`
