import os
import logging

logger = logging.getLogger("google_adk." + __name__)


def parse_billing_document(file_path: str) -> str:
    """Parses and structures text contents from invoice PDF documents or charge screenshot images.

    Args:
        file_path: The absolute local file path or GCS URI (gs://...) of the target
          invoice/screenshot.

    Returns:
        Structured markdown text showing billing records, totals, charge dates, and anomalies.
    """
    logger.info(f"Invoking parse_billing_document on file: {file_path}")

    # 1. Verification of File Existence
    if not file_path:
        return "Error: No file path provided."

    # Check if this is a GCS URI or a local path
    is_gcs = file_path.startswith("gs://")

    # Standard fallback mock invoice data
    mock_invoice_data = """
# INVOICE ANALYSIS RESULT (MOCK FALLBACK)
* **Invoice Reference**: INV-2026-0892
* **Issue Date**: May 15, 2026
* **Account Name**: John Doe (john.doe@example.com)
* **Billed Amount**: $129.00
* **Discrepancy Details**: 
  * Charge 1: May 15, 2026 - $129.00 (Status: Settled, Transaction ID: TXN-44910)
  * Charge 2: May 15, 2026 - $129.00 (Status: Settled, Transaction ID: TXN-44911)
* **Analysis**: Double billing detected for the exact same reference package on the same day. Refund of $129.00 is justified.
"""

    if not is_gcs and not os.path.exists(file_path):
        logger.warning(
            f"File {file_path} not found locally. Returning mock invoice profile for demo purposes."
        )
        return mock_invoice_data

    # 2. Extract using Google GenAI / Cloud Vision API (if configured)
    api_key = os.getenv("GOOGLE_API_KEY")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")

    if api_key or project:
        try:
            from google.genai import Client
            from google.genai import types

            # Setup client
            if project:
                # Use Google Vertex AI (Authenticated GCP scope)
                client = Client()
            else:
                # Use standard API Key
                client = Client(api_key=api_key)

            # Use the lightweight gemini-2.5-flash vision capabilities to structure the invoice
            model_name = "gemini-2.5-flash"

            prompt = """Analyze this invoice or screenshot and return a structured markdown list containing:
            1. Invoice Reference / Invoice ID
            2. Issue Date
            3. Customer Name / Account Name
            4. Billed Amount / Total
            5. Discrepancy details (e.g. if the same amount is shown charged twice on the same day).
            Keep the output brief and direct."""

            # Read image/file data
            if is_gcs:
                part = types.Part.from_uri(
                    file_uri=file_path, mime_type="application/pdf"
                )
            else:
                # Local lookup (read bytes)
                mime = "image/png"
                if file_path.lower().endswith(".pdf"):
                    mime = "application/pdf"
                elif file_path.lower().endswith(".jpg") or file_path.lower().endswith(
                    ".jpeg"
                ):
                    mime = "image/jpeg"

                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                part = types.Part.from_bytes(data=file_bytes, mime_type=mime)

            logger.info(
                "Sending multimodal prediction request to Cloud Vision API (Gemini)"
            )
            response = client.models.generate_content(
                model=model_name, contents=[part, prompt]
            )

            if response.text:
                return f"# PARSED DOCUMENT ANALYSIS\n\n{response.text}"
        except Exception as e:
            logger.error(
                f"Failed parsing via Google GenAI Vision API: {e}. Falling back to mock layout."
            )

    return mock_invoice_data
