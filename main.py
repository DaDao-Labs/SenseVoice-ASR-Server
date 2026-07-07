import os
import subprocess
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SenseVoice ASR Service")

# API Key configuration: load from environment variable or use default
API_KEY = os.getenv("SENSEVOICE_API_KEY", "MySuperSafeApiKey")

# Binary and model paths, modify according to your actual directory
BIN_PATH = "./funasr-llamacpp-linux-x64/llama-funasr-sensevoice"
MODEL_PATH = "./funasr-llamacpp-linux-x64/gguf/sensevoice-small-q8.gguf"
VAD_PATH = "./funasr-llamacpp-linux-x64/gguf/fsmn-vad.gguf"

def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key"""
    if x_api_key is None or x_api_key != API_KEY:
        logger.warning("API key verification failed")
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "msg": "Invalid API key"}
        )

@app.post("/asr", summary="Audio to Text Transcription Endpoint")
async def transcribe_audio(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    # Verify API key
    verify_api_key(x_api_key)
    
    logger.info(f"Received audio file: {file.filename}")
    
    # Save uploaded audio to temporary file
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        # Build command for transcription (parameter order: binary -a audio -m model --vad vad_model)
        cmd = [
            BIN_PATH,
            "-a", tmp_path,
            "-m", MODEL_PATH,
            "--vad", VAD_PATH
        ]
        
        # Execute binary and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=35
        )
        if result.returncode != 0:
            logger.error(f"Transcription failed, return code: {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return JSONResponse(
                status_code=500,
                content={"code": 500, "msg": "Transcription failed", "stderr": result.stderr}
            )
        
        # Extract transcription text (filter logs, get the last line of text)
        lines = result.stdout.strip().splitlines()
        text = ""
        for line in lines:
            if not line.startswith("[sensevoice]"):
                text = line
        
        return {
            "code": 0,
            "text": text,
            "raw_log": result.stdout
        }
    finally:
        os.unlink(tmp_path)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    # host=0.0.0.0 allows access from LAN/internet
    uvicorn.run(app, host="0.0.0.0", port=8000)