# Multi-Modal LLM Image-to-Text on Modal

A multi-modal Large Language Model (LLM) application deployed on Modal.com that can process images and generate text descriptions using InternVL 2.5-78B with LMDeploy.

## Overview

This project demonstrates how to deploy InternVL 2.5-78B, a state-of-the-art multi-modal LLM, on Modal.com using LMDeploy for efficient inference. The application leverages InternVL's powerful visual understanding capabilities to generate detailed and accurate text descriptions from images. It's designed to be easily deployable and scalable, taking advantage of Modal's serverless GPU infrastructure.

The implementation uses the InternVL 2.5-78B model, which offers superior performance and capabilities compared to smaller models. The model is deployed on multiple A100 GPUs with tensor parallelism for optimal inference speed and efficiency. LMDeploy is used for model deployment, providing optimized inference performance.

## Features

- Process images and generate high-quality text descriptions using InternVL 2.5-78B
- Advanced visual understanding and reasoning capabilities with state-of-the-art performance
- Deployed as a serverless application on Modal.com
- Multi-GPU A100 acceleration with tensor parallelism for optimal inference speed
- LMDeploy optimization for efficient model serving
- Simple REST API for easy integration
- Caching of model weights for faster startup

## Prerequisites

- Python 3.10+
- Modal.com account
- Modal CLI installed and configured

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/multi-llm-img-to-text-on-modal.git
   cd multi-llm-img-to-text-on-modal
   ```

2. Install the required dependencies using uv:
   ```
   uv pip install -e .
   ```

3. Configure your Modal account:
   ```
   modal token new
   ```

## Development with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. uv is a fast Python package installer and resolver.

## Modal API

This project uses Modal version 0.74.15, which has updated API compared to earlier versions. The code has been updated to use the current Modal API, which no longer uses Stubs. If you're familiar with earlier versions of Modal, note that the API has changed significantly.

## Deployment

Deploy the application to Modal.com:

```
modal deploy src/lmdeploy/server.py
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

### LMDeploy API Server

For advanced usage, you can also interact directly with the LMDeploy API server:

```python
from openai import OpenAI

client = OpenAI(api_key='YOUR_API_KEY', base_url='https://multimodal-internvl2-5-78b--serve.modal.run/v1')
model_name = client.models.list().data[0].id
response = client.chat.completions.create(
    model=model_name,
    messages=[{
        'role': 'user',
        'content': [{
            'type': 'text',
            'text': 'describe this image',
        }, {
            'type': 'image_url',
            'image_url': {
                'url': 'https://path/to/your/image.jpg',
            },
        }],
    }],
    temperature=0.8,
    top_p=0.8)
print(response)
```

## Model Information

The application uses [InternVL 2.5-78B](https://github.com/OpenGVLab/InternVL), a state-of-the-art Multimodal Large Language Model from OpenGVLab. InternVL 2.5-78B is the largest model in the InternVL 2.5 family, offering superior performance in understanding and generating text based on visual inputs, providing high-quality image descriptions, visual reasoning, and multimodal understanding.

The model is deployed using [LMDeploy](https://github.com/InternLM/lmdeploy), a toolkit for compressing, deploying, and serving LLMs & VLMs. LMDeploy provides optimized inference performance through techniques like tensor parallelism and efficient memory management.

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
- Simplified deployment process
- Streaming output capabilities

## Project Structure

- `src/lmdeploy/server.py`: Main Modal application file for building and deploying to Modal
- `src/client.py`: Example client for interacting with the deployed application
- `pyproject.toml`: Project configuration and dependencies
- `.junie/`: Directory for project guidelines and documentation

## Contributing

Please see the [guidelines](.junie/guidelines.md) for contributing to this project.

## License

This project is licensed under the terms of the LICENSE file included in the repository.
