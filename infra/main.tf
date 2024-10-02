variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "huawei-binacloud"
}

provider "google" {
    project     = var.project_id
    region      = "asia-southeast1"
    zone = "asia-southeast1-a"
}

resource "google_storage_bucket" "this" {
    name = "binacloud_registry"
    location = "ASIA-SOUTHEAST1"
    force_destroy = true
}



# # Upload Python source code to the bucket (uploads all files in the `my-python-app` directory)
# resource "google_storage_bucket_object" "python_source_code" {
#   name   = "source.zip"
#   bucket = google_storage_bucket.source_code.name
#   source = "${path.module}/my-python-app" # Path to your local directory containing Python source code
# }

# resource "google_cloudbuild_trigger" "build_docker_image" {
#   filename = "cloudbuild.yaml"
#   source_to_build {
#     uri       = "https://github.com/ruihan00/huawei-poc"
#     ref       = "refs/heads/main"
#     repo_type = "GITHUB"
#   }
# 
# }

