# ================================================================================
# Bucket for videos
# ================================================================================
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
  description  = "Account for all storage stuff"
}
resource "google_storage_bucket_iam_member" "bucket_writer" {
  bucket = google_storage_bucket.events.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.bucket_service_account.email}"
}

# ================================================================================
# Firestore for events
# ================================================================================
resource "google_firestore_database" "events" {
  name        = "(default)" # THIS IS A MUST NAME
  location_id = var.region
  type = "FIRESTORE_NATIVE"
}

resource "google_project_iam_binding" "firestore_sa_binding" {
  project = var.project_id
  role    = "roles/datastore.owner"

  members = [
    "serviceAccount:${google_service_account.bucket_service_account.email}"
  ]
}
