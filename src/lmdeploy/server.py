import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

from modal import App, Image, Volume, web_server, Secret, concurrent

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
            #ignore_patterns=["*.pt", "*.bin", "consolidated.safetensors"],
            token=hf_token,
        )
        print(f"Successfully downloaded model {model_name}")
    except Exception as e:
        print(f"Error downloading model: {e}")
        raise

########## CONSTANTS ##########

# Define model for serving
# MODEL_NAME = "OpenGVLab/InternVL2_5-78B"
# SERVE_MODEL_NAME = "internvl2_5-78b"

# MODEL_NAME = "OpenGVLab/InternVL2_5-38B-AWQ"
# SERVE_MODEL_NAME = "internvl2_5-38b-awq"

# MODEL_NAME = "OpenGVLab/InternVL2_5-8B-AWQ"
# SERVE_MODEL_NAME = "internvl2_5-8b-awq"

MODEL_NAME = "OpenGVLab/InternVL3-38B-AWQ"
SERVE_MODEL_NAME = "internvl3-38b-awq"

# MODEL_NAME = "OpenGVLab/InternVL3-14B-AWQ"
# SERVE_MODEL_NAME = "internvl3-14b-awq"

# MODEL_NAME = "OpenGVLab/InternVL3-8B-AWQ"
# SERVE_MODEL_NAME = "internvl3-8b-awq"

MODEL_DIR = f"/models/{MODEL_NAME}"
TURBOMIND_MODEL_DIR = f"/models/turbomind/{MODEL_NAME}"
# GPU = "L4"
# GPU = "L40S"
# GPU = "A100-40GB"
# GPU = "A100-40GB"
GPU = "H100"

# Define volumes for caching
#hf_cache_vol = Volume.from_name(f"huggingface-cache-{SERVE_MODEL_NAME}", create_if_missing=True)
# TODO: Not sure if this is useful, lmdeploy doesn't seem to create a cache
#lmdeploy_cache_vol = Volume.from_name("lmdeploy-cache", create_if_missing=True)

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
    .run_function(
        download_hf_model,
        timeout=60 * 60,
        kwargs={"model_dir": MODEL_DIR, "model_name": MODEL_NAME},
        # gpu=GPU,
        secrets=[hf_secret],
    )
    # everything after this is not necessary for the image download step
    .pip_install(  # add flash-attn
        "flash-attn==2.7.4.post1", extra_options="--no-build-isolation",
    )
    .pip_install(
        "timm==1.0.15",
    )
    # We can't convert vlms with lmdeploy convert manually because the serve command doesn't load the Vision part when providin a converted model
    # So I don't see a way to speed up the conversion this way
    # .run_commands(
    #     f"lmdeploy convert "
    #     f"--model-format awq "
    #     f"--dst-path {TURBOMIND_MODEL_DIR} "
    #     f"--tp 1 "
    #     #f"--tokenizer-path {MODEL_DIR}/tokenizer.model "
    #     #f"--group-size 128 "
    #     f"dummy_model_name_arg " # Use a placeholder its ignored but required syntactically
    #     f"{MODEL_DIR} ",
    #     gpu=GPU
    # )
)

########## APP SETUP ##########

app = App(f"multimodal-{SERVE_MODEL_NAME}")

SERVER_PORT = 23333

@app.function(
    image=image,
    # enable_memory_snapshot=True,
    gpu=GPU,
    cpu=1.5,
    # memory=2048,
    memory=4096,
    scaledown_window=45,
    timeout=120,
    # https://modal.com/docs/guide/concurrent-inputs
    max_containers=1,  # fix at 1 to test concurrency within 1 server setup
    volumes={
        # "/root/.cache/huggingface": hf_cache_vol,
        # "/root/.cache/lmdeploy": lmdeploy_cache_vol,
    },
    secrets=[hf_secret],  # Pass the HF_TOKEN secret to the container
)
@concurrent(max_inputs=20)  # max concurrent input into container
@web_server(port=SERVER_PORT, startup_timeout=60 * 60)
def serve():
    """Start the LMDeploy API server with OpenAI-compatible interface."""
    print("Starting LMDeploy API server...")
    # --chat-template internvl2_5 -> this is because lmdeploy at version 0.7.3 doesn't yet have internVL3 as supported model
    cmd = f"""
    lmdeploy serve api_server \
        --model-name {SERVE_MODEL_NAME} \
        --server-port {SERVER_PORT} \
        --backend turbomind \
        --session-len 16384 \
        --tp 1 \
        --model-format awq \
        --quant-policy 8 \
        --cache-max-entry-count 0.5 \
        --enable-prefix-caching \
        --chat-template internvl2_5 \
        {MODEL_DIR}
    """

    # --model-format awq \ # this is only needed for AWQ models
    # --quant-policy 8 \ # Maybe this isn't so good at all, not sure
    print(cmd)

    subprocess.Popen(cmd, shell=True)

