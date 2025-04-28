import subprocess
import json

def run_cli(command, capture_output=True):
    """Helper to run a CLI command and optionally capture JSON output."""
    result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {command}\n{result.stderr}")
    return result.stdout.strip()

def azure_deploy(
    registry_name,
    image_name,
    env_name,
    app_name,
    group_name="mygroup",
    path_to_dockerfile="Dockerfile",
    path_to_app="."
):
    # 1. Get the current default subscription
    account_info = json.loads(run_cli("az account show --output json"))
    subscription_id = account_info['id']
    print(f"Using Default Subscription ID: {subscription_id}")

    # 2. Set the subscription (redundant but safe)
    run_cli(f"az account set --subscription {subscription_id}")

    # 3. Create resource group
    run_cli(f"az group create --name {group_name} --location eastus")
    
    # 4. Create ACR (Azure Container Registry)
    run_cli(f"az acr create --name {registry_name} --resource-group {group_name} --sku standard --admin-enabled true")

    # 5. Build Docker image and push to ACR
    run_cli(f'az acr build --file "{path_to_dockerfile}" --registry {registry_name} --image {image_name} "{path_to_app}"')

    # 6. Create container app environment
    run_cli(f"az containerapp env create --name {env_name} --resource-group {group_name} --location eastus")

    # 7. Ensure ACR admin is enabled
    run_cli(f"az acr update -n {registry_name} --admin-enabled true")

    # 8. Get ACR credentials
    credentials = json.loads(run_cli(f"az acr credential show --name {registry_name}"))
    username = credentials['username']
    password = credentials['passwords'][0]['value']
    print(f"ACR Credentials retrieved.")

    # 9. Deploy the container app
    run_cli(
        f"az containerapp create "
        f"--name {app_name} "
        f"--resource-group {group_name} "
        f"--environment {env_name} "
        f"--image {registry_name}.azurecr.io/{image_name}:latest "
        f"--target-port 8080 "
        f"--ingress 'external' "
        f"--registry-server {registry_name}.azurecr.io "
        f"--registry-username {username} "
        f"--registry-password {password}"
    )

    # 10. Get and print the app URL
    fqdn = run_cli(
        f"az containerapp show "
        f"--name {app_name} "
        f"--resource-group {group_name} "
        f"--query properties.configuration.ingress.fqdn "
        f"--output tsv"
    )
    print(f"App deployed at: http://{fqdn}")

# Example usage:
azure_deploy("cloudazuretest2", "myimage2", "example-env0", "example-container-app0",path_to_dockerfile="/Users/ezra/Documents/GitHub 2/cloud-agnostic/flaskApp/Dockerfile",
    path_to_app="/Users/ezra/Documents/GitHub 2/cloud-agnostic/flaskApp/")
