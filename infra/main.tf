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

