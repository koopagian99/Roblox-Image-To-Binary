from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from PIL import Image
import io
import logging
import base64

app = Flask(__name__)
CORS(app, origins=["https://koopagian99.github.io", "https://www.roblox.com"])  # Allow requests from your GitHub Pages domain

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/decode', methods=['GET'])
def decode():
    asset_id = request.args.get('id')
    
    if not asset_id:
        logging.error('No asset ID provided')
        return jsonify({'error': 'Asset ID is required'}), 400

    # Log the Referer and Origin headers to see where the request is coming from
    referer = request.headers.get('Referer')
    origin = request.headers.get('Origin')

    if referer:
        logging.info(f'Referer: {referer}')
    if origin:
        logging.info(f'Origin: {origin}')
    
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
            logging.info(f'Generating pixel data for image {width}x{height}...')
            
            yield f'{{"size": {{"x": {width}, "y": {height}}}, "pixels": ['
            buffer = []
            total_pixels = 0  # Keep track of the total number of pixels processed
            first_chunk = True
        
            # Iterate over the image pixels
            for r, g, b, a in image.getdata():
                # Add RGBA values to the buffer
                buffer.extend([r, g, b, a])
                total_pixels += 1
        
                # If the buffer has 1024 pixels (4096 values), yield the buffer
                if len(buffer) >= 4096:  # 1024 pixels * 4 values (RGBA)
                    if not first_chunk:
                        yield ','  # Add a comma before the next chunk
                    first_chunk = False
                    logging.debug(f'Yielding 1024 pixels (4096 values), total processed: {total_pixels}')
                    yield ','.join(map(str, buffer))  # Join buffer into a string without extra comma
                    buffer = []  # Reset the buffer
        
            # Yield any remaining pixels in the buffer (even if they're less than 1024 pixels)
            if buffer:
                if not first_chunk:
                    yield ','  # Add a comma before the final chunk
                logging.debug(f'Yielding remaining pixels, total processed: {total_pixels}')
                yield ','.join(map(str, buffer))
        
            yield ']}'
            logging.info(f'Total pixels processed: {total_pixels}')
            
            logging.info('Generated pixel data sent back to client')

        return Response(generate_chunks(), content_type='application/json')
    except Exception as e:
        logging.error(f'Error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
