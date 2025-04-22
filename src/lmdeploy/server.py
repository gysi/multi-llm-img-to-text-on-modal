import subprocess
import io
import base64
from PIL import Image as PILImage

from modal import App, Image, Volume, web_endpoint, method, gpu, web_server

########## CONSTANTS ##########

# Define model for serving
MODEL_NAME = "OpenGVLab/InternVL2_5-78B"
MODEL_DIR = f"/models/{MODEL_NAME}"
SERVE_MODEL_NAME = "internvl2_5-78b"
SECONDS = 60  # for timeout

# Define volumes for caching
hf_cache_vol = Volume.from_name("huggingface-cache", create_if_missing=True)
lmdeploy_cache_vol = Volume.from_name("lmdeploy-cache", create_if_missing=True)

########## UTILS FUNCTIONS ##########

def download_hf_model(model_dir: str, model_name: str):
    """Retrieve model from HuggingFace Hub and save into
    specified path within the modal container.

    Args:
        model_dir (str): Path to save model weights in container.
        model_name (str): HuggingFace Model ID.
    """
    import os
    from huggingface_hub import snapshot_download

    os.makedirs(model_dir, exist_ok=True)

    snapshot_download(
        model_name,
        local_dir=model_dir,
        ignore_patterns=["*.pt", "*.bin"],
        token=os.environ.get("HF_TOKEN"),
    )

########## IMAGE DEFINITION ##########

# Define the Modal image with necessary dependencies
image = (
    Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch==2.6.0",
        "transformers==4.51.3",
        "pillow==11.2.1",
        "lmdeploy==0.7.3",
        "huggingface_hub[hf_transfer]==0.30.2",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})  # faster model transfers
)

########## APP SETUP ##########

app = App("multimodal-internvl2-5-78b")

NO_GPU = 1  # Number of GPUs to use
SERVER_PORT = 23333  # Port for the LMDeploy API server


@app.function(
    image=image.run_function(
        download_hf_model,
        timeout=60 * SECONDS,
        kwargs={"model_dir": MODEL_DIR, "model_name": MODEL_NAME},
    ),
    gpu=gpu.A100(count=NO_GPU, size="80GB"),
    container_idle_timeout=20 * SECONDS,
    # https://modal.com/docs/guide/concurrent-inputs
    concurrency_limit=1,  # fix at 1 to test concurrency within 1 server setup
    allow_concurrent_inputs=256,  # max concurrent input into container
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/lmdeploy": lmdeploy_cache_vol,
    },
)
@web_server(port=SERVER_PORT, startup_timeout=60 * SECONDS)
def serve():
    """Start the LMDeploy API server."""
    cmd = f"""
    lmdeploy serve api_server {MODEL_DIR} \
        --model-name {SERVE_MODEL_NAME} \
        --server-port {SERVER_PORT} \
        --session-len 8192
    """
    subprocess.Popen(cmd, shell=True)


# @app.function(
#     image=image,
#     gpu=gpu.A100(count=1),  # Only need 1 GPU for processing a single image
#     timeout=300,  # 5 minutes
#     volumes={
#         "/root/.cache/huggingface": hf_cache_vol,
#         "/root/.cache/lmdeploy": lmdeploy_cache_vol,
#     },
# )
# @method()
# def process_image(image_data):
#     """Process an image and generate a text description using the LMDeploy pipeline."""
#     # Import here to avoid loading these modules on startup
#     from lmdeploy import pipeline, TurbomindEngineConfig
#     from lmdeploy.vl import load_image
#
#     # Decode base64 image
#     image_bytes = base64.b64decode(image_data)
#     image = PILImage.open(io.BytesIO(image_bytes))
#
#     # Configure the engine with tensor parallelism
#     engine_config = TurbomindEngineConfig(session_len=8192, tp=1)
#
#     # Load the model using LMDeploy's pipeline
#     pipe = pipeline(
#         MODEL_NAME,
#         backend_config=engine_config
#     )
#
#     # Process the image with LMDeploy
#     prompt = "describe this image in detail"
#     response = pipe((prompt, image))
#
#     # Extract the generated text
#     generated_text = response.text
#
#     return {"description": generated_text}
#
#
# @app.function(
#     image=image,
#     gpu=gpu.A100(count=1),  # Only need 1 GPU for processing a single image
#     timeout=300,  # 5 minutes
#     volumes={
#         "/root/.cache/huggingface": hf_cache_vol,
#         "/root/.cache/lmdeploy": lmdeploy_cache_vol,
#     },
# )
# @web_endpoint(method="POST")
# def web_process_image(image_data: str):
#     """Web endpoint for processing images."""
#     return process_image.remote(image_data)

