from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script import InstagramAudioExtractor
from identify import recognize_local_song

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
CORS(app)

# Ensure downloads directory exists
DOWNLOAD_DIR = '/tmp/downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_reel', methods=['POST'])
def process_reel():
    try:
        reel_url = request.json.get('url')
        
        if not reel_url:
            return jsonify({
                'status': 'error', 
                'message': 'No URL provided'
            }), 400
        
        # Initialize extractor with temporary directory
        extractor = InstagramAudioExtractor(output_dir=DOWNLOAD_DIR)
        
        # Download audio
        audio_path = extractor.download_audio(reel_url)
        
        # Recognize song
        try:
            result = recognize_local_song(audio_path + ".mp3")
            
            # Clean up downloaded files
            if os.path.exists(audio_path + ".mp3"):
                os.remove(audio_path + ".mp3")
            
            return jsonify({
                'status': 'success',
                'song_name': result['track']['title'],
                'artist_name': result['track']['subtitle']
            })
        
        except Exception as e:
            # Clean up in case of recognition failure
            if os.path.exists(audio_path + ".mp3"):
                os.remove(audio_path + ".mp3")
            
            return jsonify({
                'status': 'error',
                'message': 'Unable to recognize the song'
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True)