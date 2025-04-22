# Multi-Modal LLM Image-to-Text on Modal

A multi-modal Large Language Model (LLM) application deployed on Modal.com that can process images and generate text descriptions using InternVL 2.5-78B with LMDeploy.

## Overview

This project demonstrates how to deploy InternVL 2.5-78B, a state-of-the-art multi-modal LLM, on Modal.com using LMDeploy for efficient inference. The application leverages InternVL's powerful visual understanding capabilities to generate detailed and accurate text descriptions from images. It's designed to be easily deployable and scalable, taking advantage of Modal's serverless GPU infrastructure.

The implementation uses the InternVL 2.5-78B model, which offers superior performance and capabilities compared to smaller models. The model is deployed using the official LMDeploy Docker image (openmmlab/lmdeploy:v0.7.3-cu12) and provides an OpenAI-compatible API interface for easy integration. LMDeploy's API server allows for efficient model serving with tensor parallelism for optimal inference speed.

## Features

- Process images and generate high-quality text descriptions using InternVL 2.5-78B
- Advanced visual understanding and reasoning capabilities with state-of-the-art performance
- Deployed as a serverless application on Modal.com
- A100 GPU acceleration with tensor parallelism for optimal inference speed
- Official LMDeploy Docker image for consistent and reliable deployment
- OpenAI-compatible API interface for easy integration with existing tools
- Simple REST API for direct image processing
- Caching of model weights for faster startup

## Prerequisites

- Python 3.10+
- Modal.com account
- UV installed [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- Hugging Face account with access token (for downloading the model)
- Modal secret named "huggingface-secret" containing your Hugging Face token (see [Deployment](#deployment) section)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/multi-llm-img-to-text-on-modal.git
   cd multi-llm-img-to-text-on-modal
   ```

2. Install the required dependencies using uv:
   ```
   uv sync
   ```

3. Configure your Modal account:
   ```
   modal setup
   ```

## Development with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. uv is a fast Python package installer and resolver.

## Environment Variables

This project uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```
HF_TOKEN="your_huggingface_token_here"
```

Replace `your_huggingface_token_here` with your actual Hugging Face access token. This token is used to download the model from the Hugging Face Hub.

The `.env` file is loaded automatically by the application using the python-dotenv library.

## Modal API

This project uses Modal version 0.74.15, which has updated API compared to earlier versions. The code has been updated to use the current Modal API, which no longer uses Stubs. If you're familiar with earlier versions of Modal, note that the API has changed significantly.

## Deployment

Before deploying, make sure you have set up your `.env` file with your Hugging Face token as described in the [Environment Variables](#environment-variables) section.

> **Note:** Both the model download step and the inference step require an A100-80GB GPU. Make sure your Modal account has access to this GPU type.

### Creating a Modal Secret for Hugging Face

You need to create a Modal secret named "huggingface-secret" to securely store your Hugging Face token:

```bash
modal secret create huggingface-secret --env HF_TOKEN="your_huggingface_token_here"
```

Replace `your_huggingface_token_here` with your actual Hugging Face access token. This secret will be used by the application to download the model from the Hugging Face Hub.

### Deploying the Application

Deploy the application to Modal.com using uv to ensure environment variables are loaded:

```
uv run modal deploy src/lmdeploy/server.py
```

This command uses uv to run the modal deploy command, which automatically loads the environment variables from the `.env` file.

Alternatively, you can use the `--env-file` flag:

```
uv run --env-file .env modal deploy src/lmdeploy/server.py
```

This will deploy the application and provide you with two endpoint URLs:
1. The LMDeploy API server endpoint (for direct LMDeploy API access)
2. The web_process_image endpoint (for processing images via our simplified API)

## Usage

### Using the Client

The repository includes a client script that demonstrates how to use the deployed application:

```
python src/client.py --image path/to/your/image.jpg
```

### API Endpoint

You can make direct HTTP requests to the web_process_image endpoint:

```python
import requests
import base64

# Encode the image
with open("path/to/your/image.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

# Send the request
response = requests.post(
    "https://multimodal-internvl2-5-78b--web-process-image.modal.run",
    json={"image_data": image_data}
)

# Print the result
print(response.json()["description"])
```

### LMDeploy OpenAI-Compatible API

The application uses LMDeploy's OpenAI-compatible API server, which provides an interface that's compatible with the OpenAI API. This means you can use the OpenAI Python client to interact with the model, making it easy to integrate with existing tools and workflows.

For advanced usage, you can interact directly with the LMDeploy API server:

```python
from openai import OpenAI

# The API key is set to "super-secret-key" by default in the server
client = OpenAI(api_key='super-secret-key', base_url='https://multimodal-internvl2-5-78b--serve.modal.run/v1')

# Get the available model name
model_name = client.models.list().data[0].id

# Create a chat completion request with an image
response = client.chat.completions.create(
    model=model_name,
    messages=[{
        'role': 'user',
        'content': [{
            'type': 'text',
            'text': 'describe this image in detail',
        }, {
            'type': 'image_url',
            'image_url': {
                'url': 'https://path/to/your/image.jpg',
            },
        }],
    }],
    temperature=0.7,
    top_p=0.9)

# Print the response
print(response.choices[0].message.content)
```

The API supports all the standard OpenAI API parameters, including temperature, top_p, max_tokens, etc. You can also use the API for multi-turn conversations by including previous messages in the request.

## Model Information

The application uses [InternVL 2.5-78B](https://github.com/OpenGVLab/InternVL), a state-of-the-art Multimodal Large Language Model from OpenGVLab. InternVL 2.5-78B is the largest model in the InternVL 2.5 family, offering superior performance in understanding and generating text based on visual inputs, providing high-quality image descriptions, visual reasoning, and multimodal understanding.

The model is deployed using [LMDeploy](https://github.com/InternLM/lmdeploy), a toolkit for compressing, deploying, and serving LLMs & VLMs. LMDeploy provides optimized inference performance through techniques like tensor parallelism and efficient memory management.

### Useful Resources

- [InternVL2.5 Deployment Documentation](https://internvl.readthedocs.io/en/latest/internvl2.5/deployment.html)
- [InternVL Model Family GitHub Repository](https://github.com/OpenGVLab/InternVL)
- [LMDeploy Documentation](https://lmdeploy.readthedocs.io/en/latest/index.html)
- [InternVL2.5-38B on Hugging Face](https://huggingface.co/OpenGVLab/InternVL2_5-38B)

### Model Download Optimizations

The application uses several optimizations to efficiently download the model from Hugging Face Hub:

- **Fast Downloads**: Uses `hf_transfer`, a Rust-based library developed to speed up file transfers with the Hub
- **Selective Downloading**: Filters out unnecessary files (like `.pt`, `.bin`, and `consolidated.safetensors`) to reduce download size and prevent errors
- **Error Handling**: Provides detailed error messages and progress updates during the download process
- **GPU Acceleration**: Uses an A100-80GB GPU during the download process to speed up any necessary preprocessing
- **Caching**: Utilizes Modal Volumes to cache the downloaded model weights for faster startup on subsequent deployments

### Key Features of InternVL 2.5-78B:

- Advanced visual understanding capabilities with 78B parameters
- High-quality image descriptions with exceptional detail and accuracy
- Superior reasoning about visual content
- Efficient processing of multimodal inputs
- State-of-the-art performance on vision-language tasks
- Support for multi-image and video understanding

### Benefits of LMDeploy:

- Optimized inference performance
- Efficient memory usage
- Support for tensor parallelism across multiple GPUs
- OpenAI-compatible API interface
- Simplified deployment process
- Streaming output capabilities
- Official Docker image for consistent deployment

## Project Structure

- `src/lmdeploy/server.py`: Main Modal application file for building and deploying to Modal
- `src/client.py`: Example client for interacting with the deployed application
- `pyproject.toml`: Project configuration and dependencies
- `.junie/`: Directory for project guidelines and documentation

## Contributing

Please see the [guidelines](.junie/guidelines.md) for contributing to this project.

## License

This project is licensed under the terms of the LICENSE file included in the repository.
