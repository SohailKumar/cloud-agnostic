# main.tf
variable "region" {
  default = "us-east1"
}

provider "google" {
    credentials = file("../cloudcomputingproject-453723-f176d62ddcdb.json")
    project     = "cloudcomputingproject-453723"
    region      = var.region
}   

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Create a Google Cloud Storage bucket to store the function code
resource "google_storage_bucket" "function_code_bucket" {
  name     = "function-code-bucket-${random_id.bucket_suffix.hex}"
  location = "US"
}

# Upload the function code as a zip file to the storage bucket
resource "google_storage_bucket_object" "function_code_zip" {
  name   = "function-code.zip"
  bucket = google_storage_bucket.function_code_bucket.name
  source = "../functions/function-code.zip"  # Path to the zip file of your function code
}

//Create the 
resource "google_cloudfunctions_function" "hello_world" {
    name        = "helloWorldFunction"
    description = "My Hello World Cloud Function"
    runtime     = "nodejs20" # Specify the runtime for your function (Node.js 14 in this case)
    available_memory_mb = 128 # Adjust memory as needed (128 MB for this example)

    # Define the location of the source code for the function
    source_archive_bucket = google_storage_bucket.function_code_bucket.name
    source_archive_object = google_storage_bucket_object.function_code_zip.name
    entry_point           = "helloWorld"

    # Define the trigger (in this case, an HTTP trigger)
    trigger_http = true

    # Set the function to require HTTPS (true) or allow HTTP (false)
    https_trigger_security_level = "SECURE_ALWAYS"

    # Define the region where the function will be deployed
    region = var.region
}

# Output the HTTPS URL for the Cloud Function
output "function_url" {
    value = google_cloudfunctions_function.hello_world.https_trigger_url
}