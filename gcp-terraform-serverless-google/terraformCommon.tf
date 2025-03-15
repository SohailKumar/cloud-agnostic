# mainPython.tf
variable "region" {
  default = "us-east1"
}

provider "google" {
    credentials = file("../cloudcomputingproject-453723-f176d62ddcdb.json")
    project     = "cloudcomputingproject-453723"
    region      = var.region
}   

