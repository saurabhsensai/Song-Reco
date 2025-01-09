import yt_dlp
import os
from datetime import datetime


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


# Usage example
if __name__ == "__main__":
    extractor = InstagramAudioExtractor()
    reel_url = "https://www.instagram.com/reel/DBgNLi_vOZV/?igsh=eGgwZ2M4bXdyajgz"  # Replace with actual URL
    audio_path = extractor.download_audio(reel_url)
    print(f"Audio downloaded to: {audio_path}")
