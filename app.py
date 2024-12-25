from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from PIL import Image
import io
import logging

app = Flask(__name__)
CORS(app, origins=["https://koopagian99.github.io"])  # Allow requests from your GitHub Pages domain

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/decode', methods=['GET'])
def decode():
    asset_id = request.args.get('id')
    
    if not asset_id:
        logging.error('No asset ID provided')
        return jsonify({'error': 'Asset ID is required'}), 400

    logging.info(f'Received request for asset ID: {asset_id}')
    
    try:
        # Download the image
        url = f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"
        
        logging.info(f'Downloading image from URL: {url}')
        
        response = requests.get(url)
        response.raise_for_status()

        # Decode the image
        image = Image.open(io.BytesIO(response.content))
        image = image.convert('RGBA')
        width, height = image.size

        logging.info(f'Image downloaded and decoded. Size: {width}x{height}')
        
        def generate_chunks():
            logging.info('Generating pixel data...')
            
            yield f'{{"size": {{"x": {width}, "y": {height}}}, "pixels": ['
            for i, (r, g, b, a) in enumerate(image.getdata()):
                yield f'{r},{g},{b},{a}'
                if i < (width * height - 1):
                    yield ','
            yield ']}'  # Close the JSON object

        return Response(generate_chunks(), content_type='application/json')
    except Exception as e:
        logging.error(f'Error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
