# 1. Enable Cloud Run, Artifact Registry, Cloud Build, and Org Policy APIs in Project B
resource "google_project_service" "app_services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "orgpolicy.googleapis.com"
  ])
  project            = var.app_project_id
  service            = each.key
  disable_on_destroy = false
}

# 2. Create the Service Account representing your Agent engine identity in Project B
resource "google_service_account" "run_sa" {
  project      = var.app_project_id
  account_id   = "run-agent-sa"
  display_name = "Cloud Run Agent SA"
  depends_on   = [google_project_service.app_services]
}

# 3. Create the secure IAM cross-project tunnel (Zero-Trust)
# Binds Project B's Service Account as an Authorized Prediction User on Project A
resource "google_project_iam_member" "cross_project_prediction_access" {
  project = var.model_project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.run_sa.email}"
}

# 4. Provision the Artifact Registry repository for container deployment in Project B
resource "google_artifact_registry_repository" "docker_repo" {
  project       = var.app_project_id
  location      = var.region
  repository_id = "adk-workshop"
  description   = "Repository for sovereign ADK workshop containers"
  format        = "DOCKER"

  depends_on = [google_project_service.app_services]
}

# 5. Query App Project metadata to obtain project number dynamically
data "google_project" "app_project" {
  project_id = var.app_project_id
}

# 6. Grant default Compute service account Storage Object Viewer role
# Required by Cloud Build to retrieve the source archive tarball from GCS
resource "google_project_iam_member" "compute_sa_storage_viewer" {
  project = var.app_project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${data.google_project.app_project.number}-compute@developer.gserviceaccount.com"
}

# 7. Grant default Compute service account Artifact Registry Writer role
# Required by Cloud Build to push the built Docker image to Artifact Registry
resource "google_project_iam_member" "compute_sa_registry_writer" {
  project = var.app_project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${data.google_project.app_project.number}-compute@developer.gserviceaccount.com"
}

# 8. Grant default Compute service account Logging Logs Writer role
# Required by Cloud Build to write build logs to Cloud Logging
resource "google_project_iam_member" "compute_sa_logging_writer" {
  project = var.app_project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${data.google_project.app_project.number}-compute@developer.gserviceaccount.com"
}


