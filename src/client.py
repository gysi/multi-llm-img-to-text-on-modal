import base64
import requests
import argparse
from pathlib import Path

def encode_image(image_path):
    """Encode an image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description='Client for Multi-Modal LLM API')
    parser.add_argument('--image', type=str, required=True, help='Path to the image file')
    parser.add_argument('--endpoint', type=str, default="https://multimodal-internvl2-5-78b--web-process-image.modal.run",
                        help='API endpoint URL')

    args = parser.parse_args()

    # Check if the image file exists
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file '{args.image}' not found.")
        return

    # Encode the image
    try:
        image_data = encode_image(args.image)
    except Exception as e:
        print(f"Error encoding image: {e}")
        return

    # Send the request to the API
    try:
        response = requests.post(
            args.endpoint,
            json={"image_data": image_data}
        )

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print("Image Description:")
            print(result["description"])
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error making API request: {e}")

if __name__ == "__main__":
    main()
