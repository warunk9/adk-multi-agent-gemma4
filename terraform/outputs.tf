output "vertex_endpoint_uri" {
  value       = google_vertex_ai_endpoint.gemma_endpoint.id
  description = "The deployed private sovereign Vertex AI Endpoint URI"
}

output "vertex_endpoint_id" {
  value       = element(split("/", google_vertex_ai_endpoint.gemma_endpoint.id), length(split("/", google_vertex_ai_endpoint.gemma_endpoint.id)) - 1)
  description = "The raw Endpoint ID, plug this directly into your .env"
}

output "app_service_account_email" {
  value       = google_service_account.run_sa.email
  description = "The Cloud Run Service Account email authorized to run predictions"
}

output "env_setup_helper" {
  value       = <<EOT
================================================================================
🔌 sovereign ADK Environment Configuration Helper:
================================================================================
Copy these settings directly into your customer_support/.env file:

GOOGLE_CLOUD_PROJECT="${var.model_project_id}"
GOOGLE_CLOUD_LOCATION="${var.region}"
GOOGLE_GENAI_USE_VERTEXAI="True"
GEMMA_ENDPOINT_ID="${element(split("/", google_vertex_ai_endpoint.gemma_endpoint.id), length(split("/", google_vertex_ai_endpoint.gemma_endpoint.id)) - 1)}"

And update config.py:
GEMMA_MODEL="projects/${var.model_project_id}/locations/${var.region}/endpoints/${element(split("/", google_vertex_ai_endpoint.gemma_endpoint.id), length(split("/", google_vertex_ai_endpoint.gemma_endpoint.id)) - 1)}"
================================================================================
EOT
  description = "A visual setup block to plug model configurations into env files"
}
