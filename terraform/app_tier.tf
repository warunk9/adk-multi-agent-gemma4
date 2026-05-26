# 1. Enable Cloud Run and Artifact Registry APIs in Project B
resource "google_project_service" "app_services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com"
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
