variable "save-money" {
  description = "Terminate GPU?"
  type        = bool
  default     = true
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "huawei-binacloud"
}

variable "region" {
  type        = string
  default     = "asia-southeast1"
}

provider "google" {
    project = var.project_id
    region  = var.region
    zone    = "asia-southeast1-a"
}

resource "google_storage_bucket" "this" {
    name = "binacloud_registry"
    location = "ASIA-SOUTHEAST1"
    force_destroy = true
}

