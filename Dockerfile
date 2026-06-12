FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy build config files
COPY pyproject.toml README.md ./

# Install the application and all dependencies
RUN pip install --no-cache-dir -e .

# Copy application directories
COPY customer_support/ ./customer_support/
COPY distill_gemma4.py ./

# Cloud Run injects a PORT environment variable. Listen on 0.0.0.0.
ENV PORT=8080
EXPOSE 8080

# Run the ADK web server
CMD ["sh", "-c", "adk web . --host 0.0.0.0 --port $PORT --no-reload"]
