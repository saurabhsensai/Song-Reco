# app.py
import os
from flask import Flask, render_template, request, jsonify
import yt_dlp
from datetime import datetime
import requests

class InstagramAudioExtractor:
    def __init__(self, output_dir="downloads"):
        
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def get_safe_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"reel_audio_{timestamp}.mp3"

    def download_audio(self, url):
        output_path = os.path.join(self.output_dir, self.get_safe_filename())
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path

def recognize_local_song(file_path):
    url = "https://shazam-song-recognition-api.p.rapidapi.com/recognize/file"
    headers = {
        "x-rapidapi-key":  "b7f26d018fmshf859091b39a13c3p1cfd14jsnd9d2996a991d",  # Replace with your actual RapidAPI key
        "x-rapidapi-host": "shazam-song-recognition-api.p.rapidapi.com"
    }
    
    try:
        with open(file_path, 'rb') as file:
            files = {
                'file': (os.path.basename(file_path), file, 'audio/mpeg')
            }
            response = requests.post(url, headers=headers, files=files)
            
            # Add print statement to debug response
            print("API Response:", response.text)
            
            result = response.json()
            
            # Ensure track information exists
            if 'track' in result and 'title' in result['track'] and 'subtitle' in result['track']:
                return {
                    'song_name': result['track']['title'],
                    'artist_name': result['track']['subtitle']
                }
            else:
                print("No track information found in the response")
                return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except ValueError as e:
        print(f"JSON Parsing Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None

app = Flask(__name__)
extractor = InstagramAudioExtractor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_song', methods=['POST', 'GET'])
def find_song():
    reel_url = request.form.get('reel_url')
    print(reel_url)
    
    try:
        # Download audio from Instagram Reel
        audio_path = extractor.download_audio(reel_url)
        
        # Recognize the song
        song_info = recognize_local_song(audio_path)
        
        # Always remove the audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Check if song recognition was successful
        if song_info:
            return jsonify({
                'success': True,
                'song_name': song_info['song_name'],
                'artist_name': song_info['artist_name']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Could not recognize the song'
            })
    
    except Exception as e:
        # Remove audio file if it exists
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
        
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)






# Second Backup


from flask import Flask, render_template, request
from script import InstagramAudioExtractor
from identify import recognize_local_song
import time
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = None
    song_name = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        reel_url = user_input

        extractor = InstagramAudioExtractor()
        audio_path = extractor.download_audio(reel_url)
        print(audio_path+".mp3")
        time.sleep(10)
        result = recognize_local_song(audio_path+".mp3")
        song_name = result['track']['title']

    return render_template('index.html', user_input=user_input,song_name=song_name )

if __name__ == '__main__':
    app.run(debug=True)
