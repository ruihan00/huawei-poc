resource "google_storage_bucket" "events" {
  name     = "${var.project_id}-events"
  location = "ASIA-SOUTHEAST1"

  force_destroy = true

  # lifecycle_rule {
  #   action {
  #     type = "Delete"
  #   }
  #   condition {
  #     age = 30
  #   }
  # }

  uniform_bucket_level_access = true
}

