import os
import subprocess

import urllib.request
import json

GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-31b-it")

def get_gcp_token():
    # 1. Try local Metadata Server (running on Cloud Run/GKE/GCE)
    try:
        req = urllib.request.Request(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"}
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            res_data = json.loads(response.read().decode())
            token = res_data.get("access_token")
            if token:
                return token
    except Exception:
        pass

    # 2. Fall back to local gcloud CLI (for local testing)
    try:
        return subprocess.check_output(
            ["gcloud", "auth", "application-default", "print-access-token"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
    except Exception:
        pass

    return None

# Dynamic GCP IAM OAuth token auto-injection for private sovereign predictions
# Bypasses the 1-hour expiration limit by fetching a fresh ADC token dynamically on startup
if not os.getenv("OPENAI_API_KEY"):
    gcp_token = get_gcp_token()
    if gcp_token:
        os.environ["OPENAI_API_KEY"] = gcp_token


