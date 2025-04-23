import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

from modal import App, Image, Volume, web_server, Secret, concurrent

########## CONSTANTS ##########

# Define model for serving
# MODEL_NAME = "OpenGVLab/InternVL2_5-78B"
# MODEL_DIR = f"/models/{MODEL_NAME}"
# SERVE_MODEL_NAME = "internvl2_5-78b"

MODEL_NAME = "OpenGVLab/InternVL2_5-38B-AWQ"
MODEL_DIR = f"/models/{MODEL_NAME}"
SERVE_MODEL_NAME = "internvl2_5-38b-awq"

# Define volumes for caching
hf_cache_vol = Volume.from_name(f"huggingface-cache-{SERVE_MODEL_NAME}", create_if_missing=True)
# TODO: Not sure if this is useful, lmdeploy doesn't seem to use this volume
lmdeploy_cache_vol = Volume.from_name("lmdeploy-cache", create_if_missing=True)

# Create a Secret from the HF_TOKEN environment variable
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    print("Warning: HF_TOKEN environment variable not set. Model download may fail.")

# Create a Modal Secret for the HF_TOKEN
hf_secret = Secret.from_name("huggingface-secret") if not hf_token else Secret.from_dict({"HF_TOKEN": hf_token})

########## IMAGE DEFINITION ##########

# Define the Modal image using the official LMDeploy Docker image
image = (
    Image.from_registry(
        "openmmlab/lmdeploy:v0.7.3-cu12",
    )
    .pip_install( #needed when downloading model within the buildstep
        "huggingface_hub[hf_transfer]",
        "openai==1.75.0", # lmdeploy already includes a certain version of this, if there is an error later, maybe I need to exclude this line
        "python-dotenv",
        "grpclib==0.4.7",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})  # faster model transfers
    # Currently I don't want to download the model within the buildstep
    # .run_function(
    #     download_hf_model,
    #     timeout=60 * 60,
    #     kwargs={"model_dir": MODEL_DIR, "model_name": MODEL_NAME},
    #     gpu="A100-80GB",  # Add GPU for model download step
    #     secrets=[hf_secret],
    # )
    # everything after this is not necessary for the image download step
    .pip_install(  # add flash-attn
        "flash-attn==2.7.4.post1", extra_options="--no-build-isolation"
    )
    #https://github.com/OpenGVLab/InternVL/blob/main/requirements/internvl_chat.txt
    .pip_install(
        "accelerate<1",
        "bitsandbytes==0.42.0",
        "decord",
        "deepspeed>=0.13.5",
        "einops==0.6.1",
        "einops-exts==0.0.4",
        "huggingface_hub",
        "imageio",
        "numpy==1.26.4",
        "opencv-python",
        "orjson",
        "peft==0.10.0",
        "pycocoevalcap",
        "pyyaml",
        "scikit-learn>=1.2.2",
        "scipy",
        "sentencepiece==0.1.99",
        "shortuuid",
        "tensorboardX",
        "termcolor",
        "timm==0.9.12",
        # "tokenizers==0.15.1", # Removed because transformers will resolve its needed version
        "torch>=2",
        "torchvision>=0.15",
        "tqdm",
        "transformers==4.51.3", # lmdeploy needs a newer version here than the model
        "yacs",
    )
)

########## APP SETUP ##########

app = App(f"multimodal-{SERVE_MODEL_NAME}")

SERVER_PORT = 23333

@app.function(
    image=image,
    gpu="L40S",
    scaledown_window=10 * 60,
    # https://modal.com/docs/guide/concurrent-inputs
    max_containers=1,  # fix at 1 to test concurrency within 1 server setup
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/lmdeploy": lmdeploy_cache_vol,
    },
    secrets=[hf_secret],  # Pass the HF_TOKEN secret to the container
)
@concurrent(max_inputs=256)  # max concurrent input into container
@web_server(port=SERVER_PORT, startup_timeout=60 * 60)
def serve():
    """Start the LMDeploy API server with OpenAI-compatible interface."""
    print("Starting LMDeploy API server...")
    cmd = f"""
    lmdeploy serve api_server \
        --model-name {SERVE_MODEL_NAME} \
        --server-port {SERVER_PORT} \
        --session-len 16384 \
        --tp 1 \
        --cache-max-entry-count 0.2 \
        {MODEL_NAME}
    """
    subprocess.Popen(cmd, shell=True)

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

    # Get the HF_TOKEN from environment variables (provided by the Modal Secret)
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable not set. Cannot download model without authentication.")

    try:
        print(f"Downloading model {model_name} to {model_dir}...")
        # Use snapshot_download with improved filtering
        # Ignore *.pt, *.bin files and consolidated.safetensors to prevent errors
        snapshot_download(
            repo_id=model_name,
            local_dir=model_dir,
            ignore_patterns=["*.pt", "*.bin", "consolidated.safetensors"],
            token=hf_token,
        )
        print(f"Successfully downloaded model {model_name}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        raise
