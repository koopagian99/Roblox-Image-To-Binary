from flask import Flask, request, jsonify
from PIL import Image
import requests
import io

app = Flask(__name__)

@app.route('/decode', methods=['GET'])
def decode_image():
    asset_id = request.args.get('id')
    if not asset_id:
        return jsonify({"error": "No asset ID provided"}), 400

    try:
        # Fetch the image from Roblox
        url = f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"
        response = requests.get(url)
        response.raise_for_status()

        # Decode the image
        image = Image.open(io.BytesIO(response.content))
        rgba_data = [
            [image.getpixel((x, y)) for x in range(image.width)]
            for y in range(image.height)
        ]

        return jsonify({
            "width": image.width,
            "height": image.height,
            "pixels": rgba_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
