from flask import Flask, render_template, jsonify, request
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CONVERTED_FOLDER):
    os.makedirs(CONVERTED_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'video' not in request.files:
            return jsonify({'msg': 'No video part in the request', 'status': 400})

        file = request.files['video']

        if file.filename == '':
            return jsonify({'msg': 'No selected file', 'status': 400})

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Convert the video to Xvid format using FFmpeg
        converted_file_path = os.path.join(CONVERTED_FOLDER, 'converted_' + file.filename.replace('.webm', '.avi'))
        subprocess.run([
            'ffmpeg',
            '-i', file_path,
            '-c:v', 'libxvid',
            '-qscale:v', '3',
            converted_file_path
        ])

        return jsonify({'msg': 'Upload and conversion done', 'status': 200, 'file_path': converted_file_path})

    except Exception as e:
        return jsonify({'msg': str(e), 'status': 500})



if __name__ == '__main__':
    app.run(debug=True)
