from flask import Flask, request, jsonify, send_from_directory
from pytube import YouTube
import os
import re

app = Flask(__name__)

DOWNLOAD_FOLDER = '/tmp'  # Menggunakan folder /tmp untuk Vercel, karena storage terbatas

def on_progress(stream, chunk, file_handle, bytes_remaining):
    file_size = stream.filesize
    percent = (100 * (file_size - bytes_remaining)) / file_size
    print(f"Progress unduhan: {percent:.2f}%")

def download_video(url, resolution):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()

        if stream:
            stream.download(output_path=DOWNLOAD_FOLDER)
            return True, None
        else:
            return False, "Video dengan resolusi yang diminta tidak ditemukan."
    except Exception as e:
        return False, str(e)

def get_video_info(url):
    try:
        yt = YouTube(url)
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date,
        }
        return video_info, None
    except Exception as e:
        return None, str(e)

def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Parameter 'url' tidak ada dalam request."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "URL YouTube tidak valid."}), 400
    
    success, error_message = download_video(url, resolution)
    
    if success:
        return jsonify({"message": f"Video dengan resolusi {resolution} berhasil diunduh."}), 200
    else:
        return jsonify({"error": error_message}), 500

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Parameter 'url' tidak ada dalam request."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "URL YouTube tidak valid."}), 400
    
    video_info, error_message = get_video_info(url)
    
    if video_info:
        return jsonify(video_info), 200
    else:
        return jsonify({"error": error_message}), 500

@app.route('/download_video', methods=['GET'])
def download_video_file():
    filename = "example_video.mp4"  # Ganti dengan nama file yang sesuai
    return send_from_directory(directory=DOWNLOAD_FOLDER, filename=filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
