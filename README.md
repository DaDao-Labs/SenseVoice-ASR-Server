# SenseVoice ASR Server

A lightweight, CPU-based Automatic Speech Recognition (ASR) service using the SenseVoice model. Built with FastAPI and optimized for deployment via Docker to cloud platforms.

## Features

- **Simple REST API**: Easy-to-use HTTP API for audio transcription
- **CPU-Optimized with llama.cpp/GGUF**: Runs efficiently on CPU using llama.cpp runtime and GGUF model format, no GPU required
- **Cost-Effective Deployment**: CPU-only inference significantly reduces cloud deployment costs compared to GPU-based solutions
- **Multi-Language Support**: Supports Chinese, English, Japanese, Korean, Cantonese, and more
- **Voice Activity Detection (VAD)**: Built-in VAD for better transcription accuracy
- **API Key Authentication**: Secure your service with API key protection
- **Docker Ready**: Easy deployment with Docker containers

### Supported Audio Formats

- WAV
- MP3
- FLAC

## Quick Start

### Run with Docker🐬

You can find the official Docker image on [Docker **markgzhou/sensevoice-asr-server**](https://hub.docker.com/r/markgzhou/sensevoice-asr-server).

```bash
docker run -d \
  -p 8000:8000 \
  -e SENSEVOICE_API_KEY=MySuperSafeApiKey \
  --name sensevoice-service \
  markgzhou/sensevoice-asr-server:latest
```

### ☀️ Test the Service

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 🔑 Transcribe Audio

**Endpoint:** `POST /asr`

```bash
curl -X POST http://localhost:8000/asr \
  -H "x-api-key:MySuperSafeApiKey" \
  -F "file=@audio.mp3"
```

**Response:**

```json
{
  "code": 0,
  "text": "Hello, this is a test transcription.",
  "raw_log": "Hello, this is a test..."
}
```

---

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- Docker (only for containerized deployment)
- At least 1 GB RAM and 1 vCPU recommended. No GPU Required.

### Authentication

All API requests require an `x-api-key` header (case-insensitive):

## Configuration

### Environment Variables

| Variable             | Description                | Default value       |
| -------------------- | -------------------------- | ------------------- |
| `SENSEVOICE_API_KEY` | API key for authentication | `MySuperSafeApiKey` |

### Project Structure

```
SenseVoice-Server/
├── main.py                          # Main application code
├── Dockerfile                       # Docker build configuration
├── .dockerignore                    # Docker ignore rules
├── pyproject.toml                   # Python project configuration
├── funasr-llamacpp-linux-x64/       # FunASR binary and models
│   ├── llama-funasr-sensevoice      # ASR binary
│   └── gguf/                        # Model files
│       ├── sensevoice-small-q8.gguf # Quantized SenseVoice model
│       └── fsmn-vad.gguf           # VAD model
└── README.md
```

---

### Local Setup with uv (✨Recommended)

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

**Create virtual environment and install dependencies:**

```bash
uv sync
```

This command will:

- Create a `.venv` directory with the virtual environment
- Install all dependencies from `pyproject.toml`
- Generate/update `uv.lock` with exact dependency versions

**Set environment variable:**

```bash
export SENSEVOICE_API_KEY=YourSecureApiKey
```

**Run the service:**

```bash
uv run python main.py
```

The service will start on `http://0.0.0.0:8000` / `http://localhost:8000`

## Technical Details

### Model Information

- **ASR Model:** SenseVoice Small (Q8 quantized)
- **VAD Model:** FSMN-VAD
- **Runtime:** llama.cpp with GGUF format
- **Inference Engine:** CPU-optimized, no GPU dependencies
- **Framework:** FunASR with llama.cpp backend
- **Performance:** Optimized for efficient CPU inference

### Why CPU-Only?

This service leverages the [llama.cpp](https://github.com/ggerganov/llama.cpp) runtime and [GGUF](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md) model format, which are specifically designed for efficient CPU inference. This approach offers several advantages:

- **Lower Cloud Costs**: No need for expensive GPU instances; runs on standard CPU instances
- **Easier Deployment**: No GPU driver or CUDA setup required
- **Better Scalability**: CPU instances are more readily available and cost-effective for scaling
- **Quantized Models**: Q8 quantization maintains high accuracy while reducing memory footprint
- **Cross-Platform**: Works consistently across different hardware configurations

## Troubleshooting

### Container fails to start

- Ensure Docker is running
- Check that port 8000 is not already in use
- Verify the funasr binary has execute permissions

### API returns 401 error

- Verify the `x-api-key` header is included in requests (case-insensitive)
- Check that the API key matches the `SENSEVOICE_API_KEY` environment variable

### Transcription fails

- Ensure the audio file format is supported
- Check container logs: `docker logs sensevoice-service`
- Verify the audio file is not corrupted
