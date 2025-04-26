# Multi-Modal LLM Image-to-Text on Modal

A multi-modal Large Language Model (LLM) application deployed on Modal.com that can process images and generate text descriptions using InternVL with LMDeploy.

## Overview

This project demonstrates how to deploy InternVL, a multi-modal LLM, on Modal.com using LMDeploy for efficient inference. The application leverages InternVL's powerful visual understanding capabilities to generate detailed and accurate text descriptions from images. It's designed to be easily deployable and scalable, taking advantage of Modal's serverless GPU infrastructure.

The implementation uses the InternVL. The model is deployed using the LMDeploy Docker image (openmmlab/lmdeploy:v0.7.3-cu12) and provides an OpenAI-compatible API interface for easy integration. LMDeploy's API server allows for efficient model serving with tensor parallelism for optimal inference speed.

## Features

- Process images and generate high-quality text descriptions using InternVL
- Advanced visual understanding and reasoning capabilities with state-of-the-art performance
- Deployed as a serverless application on Modal.com
- Official LMDeploy Docker image for consistent and reliable deployment
- OpenAI-compatible API interface for easy integration with existing tools
- Simple REST API for direct image processing
- Caching of model weights for faster startup

## Prerequisites

- Python 3.10+
- UV installed [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- Modal.com account
- Hugging Face account with access token (for downloading the model)
- (Optional) Modal secret named "huggingface-secret" containing your Hugging Face token (see [Deployment](#deployment) section)

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

## Deployment

Before deploying, make sure you have set up your `.env` file with your Hugging Face token as described in the [Environment Variables](#environment-variables) section.

### Creating a Modal Secret for Hugging Face

(Optional) Modal secret named "huggingface-secret" to securely store your Hugging Face token:

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

This will deploy the application and provide you with the LMDeploy API server endpoint (for direct LMDeploy API access)

## Usage (TODO: This here was AI generated and probably doesn't work, I need to work on an openAPI like client)

### Using the Client

The repository includes a client script that demonstrates how to use the deployed application:

```
python src/client.py --image path/to/your/image.jpg
```

### API Endpoint (TODO: This here is just wrong.)

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

### LMDeploy OpenAI-Compatible API (TODO: This here is not tested)

The application uses LMDeploy's OpenAI-compatible API server, which provides an interface that's compatible with the OpenAI API. This means you can use the OpenAI Python client to interact with the model, making it easy to integrate with existing tools and workflows.

You can interact directly with the LMDeploy API server:

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

The application uses [InternVL](https://github.com/OpenGVLab/InternVL), Multimodal Large Language Model from OpenGVLab. InternVL offers superior performance in understanding and generating text based on visual inputs, providing high-quality image descriptions, visual reasoning, and multimodal understanding.

The model is deployed using [LMDeploy](https://github.com/InternLM/lmdeploy), a toolkit for compressing, deploying, and serving LLMs & VLMs. LMDeploy provides optimized inference performance through techniques like tensor parallelism and efficient memory management.

### Useful Resources

- [InternVL Deployment Documentation](https://internvl.readthedocs.io/en/latest/internvl2.5/deployment.html)
- [InternVL Model Family GitHub Repository](https://github.com/OpenGVLab/InternVL)
- [LMDeploy Documentation](https://lmdeploy.readthedocs.io/en/latest/index.html)
- [InternVL3-38B-AWQ on Hugging Face](https://huggingface.co/OpenGVLab/InternVL3-38B-AWQ)

## Contributing

Please see the [guidelines](.junie/guidelines.md) for contributing to this project.

## License

This project is licensed under the terms of the LICENSE file included in the repository.
