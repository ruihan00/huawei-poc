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

resource "google_storage_bucket_iam_binding" "public_access" {
  bucket = google_storage_bucket.events.name

  role    = "roles/storage.objectViewer"
  members = [
    "allUsers"
  ]
}

resource "google_service_account" "bucket_service_account" {
  account_id   = "bucket-sa"
  display_name = "bucket-sa"
  description  = "Cloud Storage service account"
}
resource "google_storage_bucket_iam_member" "bucket_writer" {
  bucket = google_storage_bucket.events.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.bucket_service_account.email}"
}

