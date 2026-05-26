import os
import subprocess

GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-31b-it")

# Dynamic GCP IAM OAuth token auto-injection for private sovereign predictions
# Bypasses the 1-hour expiration limit by fetching a fresh ADC token dynamically on startup
if not os.getenv("OPENAI_API_KEY"):
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "application-default", "print-access-token"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        os.environ["OPENAI_API_KEY"] = token
    except Exception:
        pass

