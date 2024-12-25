from flask import Flask, request, jsonify
import requests
from PIL import Image
import io
import base64

app = Flask(__name__)

@app.route('/decode', methods=['GET'])
def decode():
    asset_id = request.args.get('id')
    if not asset_id:
        return jsonify({'error': 'Asset ID is required'}), 400

    try:
        # Download the image
        url = f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"
        response = requests.get(url)
        response.raise_for_status()

        # Decode the image
        image = Image.open(io.BytesIO(response.content))
        image = image.convert('RGBA')
        width, height = image.size
        rgba_data = list(image.getdata())

        # Create buffers
        buffer_size = 1024  # Number of pixels per buffer
        buffers = [
            rgba_data[i:i + buffer_size]
            for i in range(0, len(rgba_data), buffer_size)
        ]

        # Encode buffers as base64
        encoded_buffers = [
            base64.b64encode(bytes(sum(buffer, ()))).decode('utf-8')
            for buffer in buffers
        ]

        return jsonify({
            'size': {'x': width, 'y': height},
            'buffers': encoded_buffers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
