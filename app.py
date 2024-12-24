import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from PIL import Image
from io import BytesIO

# Enable debugging and detailed logging
app = Flask(__name__)
app.debug = True  # Enable debug mode
CORS(app)  # Enable CORS for all routes

@app.route('/process', methods=['POST'])
def process_image():
    # Extract the image URL from the request
    data = request.json
    image_url = data.get('url')

    # Print the received URL for debugging
    print(f"Received image URL: {image_url}")

    # Fetch the image data from Roblox
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an error if the request fails

        # Open the image using PIL
        img = Image.open(BytesIO(response.content))

        # Convert the image to RGBA (if not already in that mode)
        img = img.convert('RGBA')

        # Extract pixel data
        pixels = img.load()

        # Prepare binary data for the top-left corner (for example)
        width, height = img.size
        binary_data = []

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                binary_data.append([r, g, b, a])

        # Return the binary data
        return jsonify({"binary_data": binary_data[:10]})  # Just return the first 10 pixels for example

    except requests.exceptions.RequestException as e:
        # Log the error and return a detailed message
        print(f"Error fetching the image: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
