resource "random_id" "bucket_suffixP" {
  byte_length = 8
}

# Create a Google Cloud Storage bucket to store the function code
resource "google_storage_bucket" "function_code_bucket_Python" {
  name     = "function-code-bucket-${random_id.bucket_suffixP.hex}" # Random suffix thing because the name needs to be globally unique or something.
  location = "US"

  lifecycle_rule {
    action {
      type = "Delete"
    }

    condition {
      age = 2
    }
  }
}

# Upload the function code as a zip file to the storage bucket
resource "google_storage_bucket_object" "function_code_zip_Python" {
  name   = "function_code_python.zip"
  bucket = google_storage_bucket.function_code_bucket_Python.name
  source = "../functions/Python/function_code_python.zip"  # Path to the zip file of your function code
}

# Deploy function resource
resource "google_cloudfunctions_function" "hello_world_Python" {
    name        = "helloWorldFunctionPython"
    runtime     = "python312" # Specify the runtime for your function (Node.js 14 in this case)
    source_archive_bucket = google_storage_bucket.function_code_bucket_Python.name
    source_archive_object = google_storage_bucket_object.function_code_zip_Python.name
    entry_point           = "hello_world" # function name in python
    trigger_http = true
    region = var.region
    
}

resource "google_cloudfunctions_function_iam_member" "invoker_Python" {
  project        = google_cloudfunctions_function.hello_world_Python.project
  region         = google_cloudfunctions_function.hello_world_Python.region
  cloud_function = google_cloudfunctions_function.hello_world_Python.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

# Output the HTTPS URL for the Cloud Function
output "function_url_Python" {
    value = google_cloudfunctions_function.hello_world_Python.https_trigger_url
}