import logging
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from PIL import Image
from io import BytesIO
import json

# Enable debugging and detailed logging
app = Flask(__name__)
app.debug = True  # Enable debug mode
CORS(app)  # Enable CORS for all routes

# Define batch size
BATCH_SIZE = 1000  # Number of pixels per batch

@app.route('/process', methods=['POST'])
def process_image():
    # Extract the image URL from the request
    data = request.json
    image_url = data.get('url')

    # Print the received URL for debugging
    print(f"Received image URL: {image_url}")

    try:
        # Fetch the image data from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error if the request fails

        # Open the image using PIL
        img = Image.open(BytesIO(response.content))

        # Convert the image to RGBA (if not already in that mode)
        img = img.convert('RGBA')

        # Extract pixel data
        width, height = img.size
        pixels = img.load()

        def generate_batches():
            # Generator function to yield batches of pixel data
            batch = []
            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]
                    batch.append([r, g, b, a])
                    if len(batch) == BATCH_SIZE:
                        yield json.dumps(batch) + "\n"
                        batch = []
            # Yield any remaining pixels in the last batch
            if batch:
                yield json.dumps(batch) + "\n"

         def start_decomp():
             
             yield json.dumps([width, height]) + "\n"
             generate_batches()
        
        # Stream the response
        return Response(start_decomp(), content_type='application/json')

    except requests.exceptions.RequestException as e:
        # Log the error and return a detailed message
        print(f"Error fetching the image: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
