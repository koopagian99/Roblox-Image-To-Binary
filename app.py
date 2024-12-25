from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from PIL import Image
import io

app = Flask(__name__)
CORS(app, origins=["https://koopagian99.github.io"])  # Allow requests from your GitHub Pages domain

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

        def generate_chunks():
            yield f'{{"size": {{"x": {width}, "y": {height}}}, "pixels": ['
            for i, (r, g, b, a) in enumerate(image.getdata()):
                yield f'{r},{g},{b},{a}'
                if i < (width * height - 1):
                    yield ','
            yield ']}'  # Close the JSON object

        return Response(generate_chunks(), content_type='application/json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
