resource "random_id" "bucket_suffixN" {
  byte_length = 8
}


# Create a Google Cloud Storage bucket to store the function code
resource "google_storage_bucket" "function_code_bucket" {
  name     = "function-code-bucket-${random_id.bucket_suffixN.hex}"
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
resource "google_storage_bucket_object" "function_code_zip" {
  name   = "function_code_node.zip"
  bucket = google_storage_bucket.function_code_bucket.name
  source = "../functions/NodeJS/function_code_node.zip"  # Path to the zip file of your function code
}

# Deploy function resource
resource "google_cloudfunctions_function" "hello_world" {
    name        = "helloWorldFunctionNode"
    runtime     = "nodejs22" # Specify the runtime for your function (Node.js 14 in this case)
    source_archive_bucket = google_storage_bucket.function_code_bucket.name
    source_archive_object = google_storage_bucket_object.function_code_zip.name
    entry_point           = "helloWorld" # function name in python
    trigger_http = true
    region = var.region
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.hello_world.project
  region         = google_cloudfunctions_function.hello_world.region
  cloud_function = google_cloudfunctions_function.hello_world.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

# Output the HTTPS URL for the Cloud Function
output "function_url" {
    value = google_cloudfunctions_function.hello_world.https_trigger_url
}