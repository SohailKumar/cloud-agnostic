import subprocess
import time
import uuid
import requests

def run_cli(command):
    print(f"\n$ {command}")
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    return result.stdout.strip()

def gcloud_deploy(image_name_base, service_name_base, path_to_app="."):
    project = "cloud-agnostic-test-1"
    region = "us-east1"
    repo = "cloud-agnostic-image-1"
    
    unique_suffix = uuid.uuid4().hex[:8]
    unique_image_name = f"{image_name_base}-{unique_suffix}"
    unique_service_name = f"{service_name_base}-{unique_suffix}"
    
    image_url = f"{region}-docker.pkg.dev/{project}/{repo}/{unique_image_name}"

    print(f"\n Submitting build: {image_url}")
    run_cli(f"gcloud builds submit --tag \"{image_url}\" \"{path_to_app}\"")

    print(f"\n Deploying to Cloud Run: {unique_service_name}")
    run_cli(
        f"gcloud run deploy \"{unique_service_name}\" "
        f"--image \"{image_url}\" "
        f"--platform managed "
        f"--region {region} "
        f"--allow-unauthenticated"
    )

    # describe_command = (
    #         f"gcloud run services describe \"{unique_service_name}\" "
    #         f"--platform managed "
    #         f"--region {region} "
    #         f"--format value(status.url)"
    # )

    # for attempt in range(30):
    #     try:
    #         url = run_cli(describe_command)
    #         if url:
    #             print(f"\n Service deployed at: {url}")
    #             return url
    #     except subprocess.CalledProcessError:
    #         print(f"Waiting for service to become ready... ({attempt + 1})")
    #         time.sleep(2)  # wait 2 seconds then retry

    # raise Exception("Service did not become ready after retries.")



def test_cloud_run_service(url):
    print(f"\n Testing service at {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if response.text.strip() == "Hello, World from Cloud Run but now with Flask!":
            print(" Correct response received!")
        else:
            print(f" Unexpected response: '{response.text.strip()}'")
    except Exception as e:
        print(f" Request failed: {e}")

def timed_deploy(image_name_base, service_name_base, path_to_app):
    print("\n Running single deployment...")
    start = time.time()
    url = gcloud_deploy(image_name_base, service_name_base, path_to_app)
    elapsed = time.time() - start
    print(f"\n Single deployment time: {elapsed:.2f} seconds")
    # test_cloud_run_service(url)

    print("\n Running 10 deployments...")
    times = []
    for i in range(10):
        img = f"{image_name_base}-{i}"
        svc = f"{service_name_base}-{i}"
        print(f"\n--- Deployment {i+1}/10: {svc} ---")
        t0 = time.time()
        url = gcloud_deploy(img, svc, path_to_app)
        t1 = time.time()
        times.append(t1 - t0)
        print(f"\n Deployment {i+1}/10 took {t1 - t0} seconds.")
        # test_cloud_run_service(url)
    
    print("\n Deployment times (in seconds):")
    for i, t in enumerate(times, 1):
        print(f"  Deployment {i}: {t:.2f}")
    print(f"\n Total time for 10 deployments: {sum(times):.2f} seconds")

if __name__ == "__main__":
    timed_deploy(
        image_name_base="myimage-cr",
        service_name_base="my-cloud-run-service",
        path_to_app="/Users/ezra/Documents/GitHub 2/cloud-agnostic/flaskApp/"
    )
