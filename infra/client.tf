resource "google_cloud_run_v2_service" "client" {
  name     = "client"
  location = "asia-southeast1"

  deletion_protection = false
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"  # Placeholder container
    }
  }
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image  # Make terraform ignore changes to the image, prevent overwriting deployment
    ]
  }
}

# Allow public access
resource "google_cloud_run_service_iam_binding" "default" {
  location = google_cloud_run_v2_service.client.location
  service  = google_cloud_run_v2_service.client.name
  role     = "roles/run.invoker"
  members = [ "allUsers" ]
}
resource "google_cloudbuild_trigger" "cloud_run_trigger" {
  name = "cloud-run-build-trigger"
  service_account = google_service_account.cloudbuild_service_account.id

  github {
    owner        = "ruihan00"  # Replace with your GitHub username or org
    name         = "huawei-poc"
    push {
      branch = "main"
    }
  }

  build {
    options {
      logging = "CLOUD_LOGGING_ONLY"
    }

    step {
      id   = "Build"
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "$_AR_HOSTNAME/$PROJECT_ID/${google_artifact_registry_repository.default.repository_id}/$_SERVICE_NAME:$COMMIT_SHA", "client", "-f", "client/Dockerfile.prod"]
    }
    step {
      id   = "Push"
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "$_AR_HOSTNAME/$PROJECT_ID/${google_artifact_registry_repository.default.repository_id}/$_SERVICE_NAME:$COMMIT_SHA"]
    }
    step {
      id   = "Deploy"
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk:slim"
      entrypoint = "gcloud"
      args = ["run", "services", "update", "$_SERVICE_NAME", "--platform=managed", "--image=$_AR_HOSTNAME/$PROJECT_ID/${google_artifact_registry_repository.default.repository_id}/$_SERVICE_NAME:$COMMIT_SHA", "--region=$_DEPLOY_REGION"]
    }
  }

  # Define substitutions, if needed (Optional)
  substitutions = {
    _DEPLOY_REGION = "asia-southeast1"
    _AR_HOSTNAME = "asia-southeast1-docker.pkg.dev"
    _PLATFORM = "managed"
    _SERVICE_NAME = google_cloud_run_v2_service.client.name
  }
}


resource "google_service_account" "cloudbuild_service_account" {
  account_id   = "cloudbuild-sa"
  display_name = "cloudbuild-sa"
  description  = "Cloud build service account"
}
resource "google_project_iam_member" "act_as" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_project_iam_member" "logs_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_artifact_registry_repository" "default" {
  repository_id = "default"
  description   = "Repository for client builds"
  format        = "DOCKER"
}

# Grant 'roles/artifactregistry.writer' to the service account at the repository level
resource "google_artifact_registry_repository_iam_member" "repo_writer" {
  repository   = google_artifact_registry_repository.default.id
  role         = "roles/artifactregistry.writer"
  member       = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}
resource "google_project_iam_member" "service_account_user" {
  project = var.project_id
  role         = "roles/run.developer"
  member       = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}
