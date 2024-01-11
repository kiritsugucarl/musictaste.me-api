from flask import Flask, request, jsonify
import math

recommend = Flask(__name__)

def calculate_similarity(user_profile, song_features):
    distance = 0
    for feature in user_profile:
        distance += (user_profile[feature] - song_features.get(feature, 0)) ** 2
        
    return math.sqrt(distance)

@recommend.route('/recommend', methods=['POST'])
def recommendSongs():
    data = request.get_json()
    
    # Get user input
    user_input = data.get('user_input', [])
    
    