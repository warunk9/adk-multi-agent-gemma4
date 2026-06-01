import os
import sys
import subprocess
from google.genai import Client
from google.genai import types

def get_adc_token():
    """Dynamic GCP OAuth token auto-injection for Vertex AI."""
    try:
        return subprocess.check_output(
            ["gcloud", "auth", "application-default", "print-access-token"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        return None

# Auto-inject OAuth token into environment to prevent 1-hour expirations
if not os.getenv("OPENAI_API_KEY"):
    token = get_adc_token()
    if token:
        os.environ["OPENAI_API_KEY"] = token

# Initialize the Google GenAI client configured for Vertex AI
client = Client(
    http_options={
        "api_version": "v1beta1"
    }
)

def launch_distillation():
    # Ensure variables are loaded
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "poc-gemma4-496922")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west1")
    
    print("🚀 Initializing Gemma 4 Distillation Pipeline on Vertex AI...")
    print(f"   Target Project: {project}")
    print(f"   Region:         {location}")

    # 1. Define Dataset URIs
    training_data_uri = "gs://poc-gemma4-496922-datasets/distill_train.jsonl"
    validation_data_uri = "gs://poc-gemma4-496922-datasets/distill_val.jsonl"
    output_model_uri = "gs://poc-gemma4-496922-tuning-artifacts/gemma-distillation-output"

    print(f"   Training Dataset:   {training_data_uri}")
    print(f"   Validation Dataset: {validation_data_uri}")

    # 2. Configure the Distillation Job Parameters
    tuning_job = client.tunings.tune(
        # The Student Model to be trained
        base_model="google/gemma-2-2b-it",
        training_dataset=types.TuningDataset(
            gcs_uri=training_data_uri,
        ),
        config=types.CreateTuningJobConfig(
            tuned_model_display_name="gemma-2b-distilled-from-gemma4-31b",
            method="DISTILLATION",
            # The Teacher Model acting as the expert
            base_teacher_model="google/gemma-4-31b-it",
            epoch_count=10,
            learning_rate_multiplier=1.0,
            batch_size=4,
            tuning_mode="TUNING_MODE_FULL",
            validation_dataset=types.TuningValidationDataset(
                gcs_uri=validation_data_uri,
            ),
            output_uri=output_model_uri
        ),
    )

    print("\n✅ Distillation Job successfully created!")
    print(f"   Job ID:      {tuning_job.name}")
    print(f"   Job State:   {tuning_job.state}")
    print(f"   Create Time: {tuning_job.create_time}")
    print("\nTo monitor this job, run:")
    print(f"   gcloud ai tuning-jobs describe {tuning_job.name} --project={project} --region={location}")

if __name__ == "__main__":
    launch_distillation()
