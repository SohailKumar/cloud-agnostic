import yaml, os, sys, subprocess

project_types = {}

def load_yaml(file):
    # Load YAML file into a dictionary
    with open(file, "r") as file:
        data = yaml.safe_load(file)  # `safe_load` prevents execution of arbitrary code

    print(data)  # Prints the dictionary representation of the YAML content
    return data

def write_docker_vars(data):
    # Extract the "docker" section and convert to Terraform map format
    docker_data = data.get("docker", {})

    terraform_variable = f'''variable "docker" {{
    type = map(string)
    default = {{
        {chr(10).join(f'    {key} = "{value}"' for key, value in docker_data.items())}
    }}
    }}
    '''

    # Write to a Terraform file
    with open("main.tf", "w") as tf_file:
        tf_file.write(terraform_variable)

def write_dockerfile():
  data =  """# Use the official Python image as a base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local code into the container
COPY . /app

# Install the required dependencies
RUN pip install Flask

# Expose port 8080 for the application
EXPOSE 8080

# Set the entry point for the application
CMD ["python", "app.py"]
  """
  with open("Dockerfile", "w") as d:
      d.write(data)

def build_container(config_path, source_dir):

  result = subprocess.run(["gcloud", "builds", "submit", "--tag", "us-east1-docker.pkg.dev/cloud-agnostic-test-1/cloud-agnostic-image-1/image1"], check=True)
  print(result.stdout)
  return result.stdout    

# def set_vars(data):
#     variable "region" {
#   default = "us-east1"
# }


def write_cloudbuild_file(data):
    with open("cloudbuild.yaml", "w") as f:
        f.write(f"""steps:
- name: 'gcr.io/cloud-builders/docker'
  args: [ 'build', '-t', '{data["docker"]["region"]}-docker.pkg.dev/{data["project-id"]}/{data["docker"]["repo"]}/{data["docker"]["image"]}', '.' ]
""")

def write_tf_file(data, container_url):
  cloud_run = """provider "google" {
  credentials = file("XXX.json")
  project     = "cloud-agnostic-test-1"
  region      = "us-east1"
}

# Cloud Run service
resource "google_cloud_run_service" "default" {
  name     = "cloud-run-service"
  location = "us-east1"

  template {
    spec {
      containers {
        image = "us-east1-docker.pkg.dev/cloud-agnostic-test-1/cloud-agnostic-image-1/image1:latest"

        resources {
          limits = {
            memory = "256Mi"
            cpu    = "1"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Enable public access to the Cloud Run service
resource "google_cloud_run_service_iam_member" "invoker" {
  service    = google_cloud_run_service.default.name
  location   = google_cloud_run_service.default.location
  role       = "roles/run.invoker"
  member     = "allUsers"
}

# Output the URL of the Cloud Run service
output "cloud_run_url" {
  value = google_cloud_run_service.default.status[0].url
}
"""#.format(container_url)
  with open("main.tf", "w") as f:
      f.write(cloud_run)

  
  
  

def run_tf_commands():
    result1 =  subprocess.run(["terraform","init"], check=True)
    result2 =  subprocess.run(["terraform","plan"], check=True)
    result3 =  subprocess.run(["terraform","apply"], check=True)


def main():
    config = load_yaml(sys.argv[1])
    write_dockerfile()
    write_cloudbuild_file(config)
    container_url = build_container("cloudbuild.yaml","./flaskApp/")
    write_tf_file(config, container_url)
    run_tf_commands()

    
if __name__ == "__main__":
    main()