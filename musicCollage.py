from flask import Flask, request, send_file, jsonify
from PIL import Image
from io import BytesIO
from flask_cors import CORS
import requests
import logging
import base64

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, origin="*")


@app.route('/recommendationCollage', methods=['POST'])
def generate_and_send_collage():
    data = request.json
    image_links = data.get('imageLinks', [])
    
    app.logger.debug(f"Received image links: {image_links}")
    
    # Generate collage
    collage = generate_collage(image_links)
    
    collage_data = BytesIO()
    collage.save(collage_data, format='JPEG')
    collage_data.seek(0)
    
    collage_base64 = base64.b64encode(collage_data.read()).decode('utf-8')
    
    return jsonify({'collage' : collage_base64})

    
def generate_collage(image_links):
    collage_width = 1080
    collage_height = 1920
    collage = Image.new("RGB", (collage_width, collage_height))
    
    num_rows = 5
    num_cols = 2
    
    cell_width = collage_width // num_cols
    cell_height = collage_height // num_rows
    
    cell_coordinates = []
    
    for row in range(num_rows):
        for col in range(num_cols):
            x_offset = col * cell_width
            y_offset = row * cell_height
            cell_coordinates.append((x_offset, y_offset))
            
    for link, (x_offset, y_offset) in zip(image_links, cell_coordinates):
        response = requests.get(link)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            img = Image.open(image_data).convert("RGB")
            # Wait for the image to be fully loaded
            img.load()

            img = img.resize((cell_width, cell_height))

            collage.paste(img, (x_offset, y_offset))
            
    return collage


if __name__ == '__main__':
    app.run(debug=True)