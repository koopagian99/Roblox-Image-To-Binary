from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_image():
    data = request.json
    image_url = data.get('url')

    if not image_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Fetch the image from the provided URL
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGBA")

        # Convert the image to binary data
        width, height = image.size
        binary_data = []

        for y in range(height):
            for x in range(width):
                r, g, b, a = image.getpixel((x, y))
                binary_data.append([r, g, b, a])

        return jsonify({"binary_data": binary_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    from os import environ
    app.run(host='0.0.0.0', port=int(environ.get('PORT', 5000)))
