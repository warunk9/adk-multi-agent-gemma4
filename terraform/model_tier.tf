# 1. Enable prediction, compute and container APIs in Project A
resource "google_project_service" "model_services" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "compute.googleapis.com",
    "container.googleapis.com"
  ])
  project            = var.model_project_id
  service            = each.key
  disable_on_destroy = false
}

# 2. Provision the Private Vertex AI Endpoint inside Project A
resource "google_vertex_ai_endpoint" "gemma_endpoint" {
  project      = var.model_project_id
  name         = "gemma4-sovereign-endpoint-v4"
  display_name = "gemma4-sovereign-endpoint-v4"
  location     = var.region

  # A. Upload and deploy model serving container when endpoint is created
  provisioner "local-exec" {
    command = <<EOT
      set -e
      echo "--------------------------------------------------------"
      echo "🚀 Starting private Gemma 4 deployment to Vertex AI..."
      echo "--------------------------------------------------------"
      
      # Determine if a Hugging Face token is provided
      ENV_VARS_ARG=""
      if [ ! -z "${var.huggingface_token}" ]; then
        ENV_VARS_ARG="--container-env-vars=HF_TOKEN=${var.huggingface_token}"
        echo "Authentication token detected, passing to vLLM boot pipeline..."
      fi

      # Upload model spec to Registry
      # Points to Google's official managed vLLM OpenAI-compatible prediction container
      echo "Uploading model config to registry..."
      MODEL_ID=$(gcloud ai models upload \
        --project=${self.project} \
        --region=${self.location} \
        --display-name="gemma-4-31b-it" \
        --container-image-uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:gemma4" \
        --container-args="python,-m,vllm.entrypoints.api_server,--host=0.0.0.0,--port=8080,--model=gs://vertex-model-garden-restricted-us/gemma4/gemma-4-31B-it,--tensor-parallel-size=4,--max-model-len=32768,--max-num-seqs=128,--gpu-memory-utilization=0.9,--limit-mm-per-prompt.image=4,--limit-mm-per-prompt.video=1,--enable-auto-tool-choice,--tool-call-parser=gemma4,--reasoning-parser=gemma4" \
        --container-health-route="/ping" \
        --container-predict-route="/generate" \
        --container-ports=8080 \
        --container-shared-memory-size-mb=65536 \
        $ENV_VARS_ARG \
        --format="value(model)")
      
      echo "Model config registered successfully. Model ID: $MODEL_ID"
      
      # Deploy Model Registry Spec to Private Endpoint
      # Deploys on a 4-card NVIDIA L4 cluster for native unquantized execution
      echo "Deploying serving container cluster to Endpoint..."
      gcloud ai endpoints deploy-model ${self.id} \
        --project=${self.project} \
        --region=${self.location} \
        --model=$MODEL_ID \
        --display-name="gemma-4-31b-it-deployed" \
        --machine-type=${var.gemma_machine_type} \
        --accelerator=type=nvidia-l4,count=4 \
        --min-replica-count=1 \
        --max-replica-count=1 \
        --traffic-split=0=100
      
      echo "--------------------------------------------------------"
      echo "✅ Gemma 4 successfully deployed on 4x NVIDIA L4 cluster!"
      echo "--------------------------------------------------------"
    EOT
  }

  # B. Automated teardown on 'terraform destroy' to prevent resource/billing leaks
  provisioner "local-exec" {
    when    = destroy
    command = <<EOT
      echo "--------------------------------------------------------"
      echo "🗑️ Initiating teardown of private sovereign model..."
      echo "--------------------------------------------------------"
      
      ENDPOINT_URI="${self.id}"
      PROJECT_ID="${self.project}"
      REGION="${self.location}"
      
      # Extract raw Endpoint ID
      ENDPOINT_ID=$(echo $ENDPOINT_URI | awk -F'/' '{print $NF}')
      
      # Find all deployed models attached to endpoint
      DEPLOYED_MODEL_ID=$(gcloud ai endpoints describe $ENDPOINT_ID \
        --project=$PROJECT_ID \
        --region=$REGION \
        --format="value(deployedModels.id)" 2>/dev/null)
      
      if [ ! -z "$DEPLOYED_MODEL_ID" ]; then
        echo "Undeploying model ID: $DEPLOYED_MODEL_ID from endpoint: $ENDPOINT_ID"
        gcloud ai endpoints undeploy-model $ENDPOINT_ID \
          --project=$PROJECT_ID \
          --region=$REGION \
          --deployed-model-id=$DEPLOYED_MODEL_ID
      else
        echo "No deployed models found on endpoint. Skipping undeployment."
      fi
      
      echo "✅ Private model teardown complete!"
    EOT
  }

  depends_on = [google_project_service.model_services]
}

