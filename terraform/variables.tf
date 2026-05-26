variable "model_project_id" {
  type        = string
  default     = "gemma4-model-dev"
  description = "GCP Project ID hosting the private Gemma 4 Model (Project A)"
}

variable "app_project_id" {
  type        = string
  default     = "agent-app-on-gemma-dev"
  description = "GCP Project ID hosting the ADK Multi-Agent Cloud Run engine (Project B)"
}

variable "region" {
  type        = string
  default     = "us-west1"
  description = "GCP Region for model prediction and app hosting"
}

variable "gemma_machine_type" {
  type        = string
  default     = "g2-standard-48"
  description = "GCP Machine type to run Gemma 4 31B (g2-standard-48 has 4x NVIDIA L4 GPUs, yielding 96GB vRAM)"
}

variable "huggingface_token" {
  type        = string
  sensitive   = true
  default     = ""
  description = "Optional: Your Hugging Face User Access Token (needed to dynamically pull unquantized Gemma weights at boot-time)"
}
