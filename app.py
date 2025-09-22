import streamlit as st
import subprocess
import os
import csv
from datetime import datetime

TFVARS_FILE = "terraform.tfvars"
TERRAFORM_DIR = os.getcwd()
HISTORY_FILE = "vm_history.csv"


if not os.path.exists(TFVARS_FILE):
    st.error("`terraform.tfvars` not found!")
    st.stop()


if "vm_created" not in st.session_state:
    st.session_state.vm_created = False
if "is_creating_vm" not in st.session_state:
    st.session_state.is_creating_vm = False


def parse_tfvars(file_path):
    vars_dict = {}
    tags_dict = {}
    inside_tags = False
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("tags = {"):
                inside_tags = True
                continue
            if inside_tags:
                if line.endswith("}"):
                    inside_tags = False
                    vars_dict["tags"] = tags_dict
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    tags_dict[key.strip()] = value.strip().strip('"')
            elif "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                vars_dict[key.strip()] = value.strip().strip('"')
    return vars_dict

def write_tfvars(config, file_path=TFVARS_FILE):
    with open(file_path, "w") as f:
        for key, value in config.items():
            if isinstance(value, dict):
                f.write(f"{key} = {{\n")
                for k, v in value.items():
                    f.write(f'  {k} = "{v}"\n')
                f.write("}\n")
            else:
                f.write(f'{key} = "{value}"\n')

def log_history(action, config):
    file_exists = os.path.isfile(HISTORY_FILE)

    with open(HISTORY_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "VM Name", "Environment", "Resource Group", "Owner", "Tag", "Action"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            config.get("vm_name", "Unknown"),
            "Windows",
            config.get("resource_group_name", "Unknown"),
            config.get("tags", {}).get("Owner", "Unknown"),
            config.get("tags", {}).get("Env", "Unknown"),
            action
        ])


def run_terraform_with_live_output(output_area):
    commands = [
        ("terraform init", ["terraform", "init"]),
        ("terraform plan", ["terraform", "plan", "-var-file=terraform.tfvars"]),
        ("terraform apply", ["terraform", "apply", "-auto-approve", "-var-file=terraform.tfvars"]),
    ]

    full_output = ""

    for label, cmd in commands:
        output_area.markdown(f"### 🔧 Running: `{label}`")
        output = ""
        with output_area.container():
            log_window = st.empty()
            process = subprocess.Popen(
                cmd,
                cwd=TERRAFORM_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )
            for line in process.stdout:
                output += line
                log_window.text_area(f"{label} Output", output, height=300)
            process.wait()
            if process.returncode != 0:
                st.error(f"❌ {label} failed.")
                st.session_state.is_creating_vm = False
                st.stop()
        full_output += output

    if "Apply complete" in full_output:
        st.success("✅ VM Created Successfully!")
        tfvars = parse_tfvars(TFVARS_FILE)
        log_history("Created", tfvars)
        st.session_state.vm_created = True
    else:
        st.error("⚠️ Terraform finished, but VM creation could not be confirmed.")

    st.session_state.is_creating_vm = False

def destroy_vm(output_area):
    output_area.warning("Destroying VM using Terraform...")
    result = subprocess.run(
        ["terraform", "destroy", "-auto-approve", "-var-file=terraform.tfvars"],
        cwd=TERRAFORM_DIR, capture_output=True, text=True
    )
    output_area.text_area("Destroy Output", result.stdout, height=300)
    if result.returncode != 0:
        output_area.error(result.stderr)
    else:
        st.session_state.vm_created = False
        tfvars = parse_tfvars(TFVARS_FILE)
        log_history("Destroyed", tfvars)
        output_area.success("✅ VM destroyed.")


st.set_page_config(layout="wide")
st.sidebar.title("🧭 Navigation")


if st.session_state.is_creating_vm:
    st.sidebar.warning("🚧 VM creation in progress. Tab switching disabled.")
    page = "Create VM"
else:
    page = st.sidebar.radio("Choose Action", ["Create VM", "Destroy VM", "History"])

st.title("☁️ Cloud Infrastructure Dashboard")

tfvars = parse_tfvars(TFVARS_FILE)


if page == "Create VM":
    st.header("🖥️ Provision Virtual Machine")

    with st.form("vm_form"):
        st.subheader("1️⃣ VM Basics")
        col1, col2 = st.columns(2)
        with col1:
            vm_name = st.text_input("VM Name", value=tfvars.get("vm_name", ""))
            vm_size = st.selectbox("VM Size", ["Standard_D2as_v5", "Standard_B2s", "Standard_DS1_v2"])
        with col2:
            location = st.selectbox("Location", ["East US", "West US", "Central US"])

        st.subheader("2️⃣ Admin Settings")
        col3, col4 = st.columns(2)
        with col3:
            admin_username = st.text_input("Admin Username", value=tfvars.get("admin_username", ""))
        with col4:
            admin_password = st.text_input("Admin Password", type="password", value=tfvars.get("admin_password", ""))

        st.subheader("3️⃣ Networking")
        col5, col6 = st.columns(2)
        with col5:
            resource_group_name = st.text_input("Resource Group Name", value=tfvars.get("resource_group_name", ""))
            vnet_name = st.text_input("VNet Name", value=tfvars.get("vnet_name", ""))
        with col6:
            subnet_name = st.text_input("Subnet Name", value=tfvars.get("subnet_name", ""))
            os_disk_type = st.selectbox("OS Disk Type", ["StandardSSD_LRS", "Premium_LRS"])

        st.subheader("4️⃣ Tags")
        col7, col8 = st.columns(2)
        with col7:
            tags_owner = st.text_input("Tag: Owner", value=tfvars.get("tags", {}).get("Owner", ""))
        with col8:
            tags_env = st.selectbox("Tag: Environment", ["Dev", "Test", "Prod"])

        submitted = st.form_submit_button("🚀 Create VM")

        if submitted:
            if len(vm_name) > 15:
                st.error("VM name must be ≤ 15 characters.")
                st.stop()

            config = {
                "subscription_id": tfvars["subscription_id"],
                "location": location,
                "resource_group_name": resource_group_name,
                "vnet_name": vnet_name,
                "subnet_name": subnet_name,
                "vm_name": vm_name,
                "vm_size": vm_size,
                "admin_username": admin_username,
                "admin_password": admin_password,
                "os_disk_type": os_disk_type,
                "tags": {
                    "Owner": tags_owner,
                    "Env": tags_env
                }
            }

            write_tfvars(config)
            st.success("Terraform configuration updated. Running Terraform...")

            st.session_state.is_creating_vm = True
            with st.spinner("⏳ Creating VM... Please wait..."):
                run_terraform_with_live_output(st)

elif page == "Destroy VM":
    st.header("🗑️ Destroy Virtual Machine")
    if st.button("⚠️ Destroy VM"):
        output = st.container()
        destroy_vm(output)

elif page == "History":
    st.header("📜 VM Action History")
    if not os.path.isfile(HISTORY_FILE):
        st.info("No history available yet.")
    else:
        with open(HISTORY_FILE, newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if not rows:
                st.info("History file is empty.")
            else:
                st.dataframe(rows[::-1])  # latest first

