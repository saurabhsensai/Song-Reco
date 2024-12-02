from flask import Flask, render_template, request, flash, redirect, url_for
from script import InstagramAudioExtractor
from identify import recognize_local_song
import time
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = None
    song_name = None
    error_message = None

    if request.method == 'POST':
        user_input = request.form['user_input']
        
        try:
            # Instagram URL Extraction
            extractor = InstagramAudioExtractor()
            audio_path = extractor.download_audio(user_input)
            
            # Wait a bit to ensure file is fully downloaded
            time.sleep(10)
            
            # Song Recognition
            try:
                result = recognize_local_song(audio_path+".mp3")
                song_name = result['track']['title']
                artist_name = result['track']['subtitle']
                
                # Optional: Clean up the downloaded audio file
                os.remove(audio_path+".mp3")
                
            except Exception as recognition_error:
                # Clean up the downloaded audio file
                if os.path.exists(audio_path+".mp3"):
                    os.remove(audio_path+".mp3")
                
                # Specific error handling for song recognition
                if 'track' not in str(recognition_error).lower():
                    error_message = "Unable to recognize the song. The audio might be too short or unclear."
                else:
                    error_message = "No song could be identified from this audio."
        
        except Exception as extraction_error:
            # Handle Instagram URL extraction errors
            error_message = "Invalid Instagram Reel URL. Please check the link and try again."
    
    return render_template('index.html', 
                           user_input=user_input, 
                           song_name=song_name, 
                           error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)