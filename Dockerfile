# Use Python 3.14 slim image as base
FROM python:3.14-slim

# Metadata
LABEL org.opencontainers.image.title="SenseVoice-ASR-Server"
LABEL org.opencontainers.image.description="SenseVoice ASR Server"
LABEL org.opencontainers.image.authors="Guanlong Zhou"
LABEL org.opencontainers.image.source="https://github.com/DaDao-Labs/SenseVoice-ASR-Server"
LABEL org.opencontainers.image.port="8000"
LABEL org.opencontainers.image.version="latest"
LABEL org.opencontainers.image.license="MIT"

# Set working directory
WORKDIR /app

# Copy funasr binary and models
COPY funasr-llamacpp-linux-x64/ ./funasr-llamacpp-linux-x64/

# Make the binary executable
RUN chmod +x ./funasr-llamacpp-linux-x64/llama-funasr-sensevoice

# Install system dependencies required for funasr binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies using pip and clear cache
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip 

# Copy application code
COPY main.py ./
COPY templates/ ./templates/


# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
# Note: SENSEVOICE_API_KEY and SENSEVOICE_TIMEOUT should be set at runtime via -e flag or docker-compose
CMD ["python", "main.py"]