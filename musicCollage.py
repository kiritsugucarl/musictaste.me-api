import requests
import logging
import base64
import spotipy
from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask_cors import CORS
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, origin="*")

SPOTIFY_CLIENT_ID = "76119cfba3a9409fbf5db1c44014b7b3"
SPOTIFY_CLIENT_SECRET = "eaf50650429f46e0b42bffabc1c02666"
sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

@app.route('/recommendationCollage', methods=['POST'])
def generate_and_send_collage():
    data = request.json
    track_ids = data.get('trackIds', [])
    
    app.logger.debug(f"Received track IDS: {track_ids}")
    # app.logger.debug(f"Received image links: {image_links}")
    
    tracks_info = get_tracks_info(track_ids)
    
    # Generate collage
    collage = generate_collage(tracks_info)
    
    collage_data = BytesIO()
    collage.save(collage_data, format='JPEG')
    collage_data.seek(0)
    
    collage_base64 = base64.b64encode(collage_data.read()).decode('utf-8')
    
    return jsonify({'collage' : collage_base64})


def get_tracks_info(track_ids):
    tracks_info = []
    
    for track_id in track_ids:
        track = sp.track(track_id)
        
        track_info = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'image': track['album']['images'][0]['url']
        }
        tracks_info.append(track_info)
        
    return tracks_info

    
def generate_collage(tracks_info):
    collage_width = 1080
    collage_height = 1920
    collage = Image.new("RGB", (collage_width, collage_height))
    
    num_rows_content = 5
    num_rows_watermark = 1
    num_cols = 2
    
    num_rows_total = num_rows_content + num_rows_watermark
    
    cell_width = collage_width // num_cols
    cell_height = collage_height // num_rows_total
    
    cell_coordinates = []
    
    collage = Image.new('RGB', (collage_width, collage_height), "#000000")
    
    draw = ImageDraw.Draw(collage)
    
    border_color = "#000000"  # Color of the borders
    border_width = 5  # Width of the borders
    image_spacing = 10  # Space between images
    
    for row in range(num_rows_total):
        for col in range(num_cols):
            x_offset = col * cell_width
            y_offset = row * cell_height
            cell_coordinates.append((x_offset, y_offset))
            
    for (track_info, (x_offset, y_offset)) in zip(tracks_info, cell_coordinates):
        print(track_info)
        print(f"Artist debug: {track_info['artist']}")
        
        # Draw rectangle (border) around each image
        draw.rectangle(
            [x_offset, y_offset, x_offset + cell_width, y_offset + cell_height],
            outline=border_color,
            width=border_width
        )
        
        # Check if 'album' key is present in track_info
        image_url = track_info['image']
        print(f"Image URL: {image_url}")
        response = requests.get(image_url)
        
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            img = Image.open(image_data).convert("RGB")
            # Wait for the image to be fully loaded
            img.load()

            img = img.resize((cell_width - 2 * border_width, cell_height - 2 * border_width))

            collage.paste(img, (x_offset + border_width + image_spacing, y_offset + border_width))
            
        if 'artist' in track_info:
            artist_name = track_info['artist']
        else:
            artist_name = "Unknown Artist"
            
        trackNameText = f"{track_info['name']} - {artist_name}"
        
        font_size = 25
        font = ImageFont.truetype("font/MuseoModerno-Bold.ttf", font_size)

        text_width = draw.textlength(trackNameText, font=font)
        text_height = font.getbbox(trackNameText)[3] - font.getbbox(trackNameText)[1]  # Calculate height using bottom and top coordinates
        text_padding_x = 5
        text_padding_y = 30
        
        text_color = "#f1f1f1"
        text_position = (
            x_offset + text_padding_x + (cell_width - text_width - 2 * text_padding_x) / 2,
            y_offset + cell_height - text_padding_y - text_height
        )
        draw.text(text_position, trackNameText, fill=text_color, font=font)
        
        # watermark_font_size = 40
        # watermark_font = ImageFont.truetype("font/MuseoModerno-Bold.ttf", watermark_font_size)     
            
        # watermark_text = "Produced by musictaste.me"
        # watermark_y_offset = num_rows_content * cell_height
        
        # watermark_text_width = draw.textlength(watermark_text, font=watermark_font)
        # watermark_text_height = font.getbbox(watermark_text)[3]  - font.getbbox(watermark_text)[1]
        # watermark_x_offset = (collage_width - watermark_text_width) // 2
        # draw.text((watermark_x_offset, watermark_y_offset), watermark_text, font=watermark_font, fill="#f1f1f1")
            
    return collage


if __name__ == '__main__':
    app.run(debug=True)