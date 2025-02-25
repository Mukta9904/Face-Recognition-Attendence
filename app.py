from flask import Flask, render_template, jsonify, request
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
FRAME_FOLDER = 'frames'
RECOGNIZE_FOLDER = 'recognize'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(FRAME_FOLDER):
    os.makedirs(FRAME_FOLDER)
if not os.path.exists(RECOGNIZE_FOLDER):
    os.makedirs(RECOGNIZE_FOLDER)

# Counter to keep track of saved frames
frame_counter = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global frame_counter
    try:
        if 'video' not in request.files:
            return jsonify({'msg': 'No video part in the request', 'status': 400})

        file = request.files['video']

        if file.filename == '':
            return jsonify({'msg': 'No selected file', 'status': 400})

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the video to extract the best frame
        best_frame = extract_best_frame(file_path)

        if best_frame is not None:
            frame_path = os.path.join(FRAME_FOLDER, f'best_frame_{frame_counter}.jpg')
            cv2.imwrite(frame_path, best_frame)
            frame_counter += 1
            return jsonify({'msg': 'Best frame extracted and saved', 'status': 200, 'frame_path': frame_path})
        else:
            return jsonify({'msg': 'Failed to extract best frame', 'status': 500})

    except Exception as e:
        return jsonify({'msg': str(e), 'status': 500})

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    global frame_counter
    try:
        if 'video' not in request.files:
            return jsonify({'msg': 'No video part in the request', 'status': 400})

        file = request.files['video']

        if file.filename == '':
            return jsonify({'msg': 'No selected file', 'status': 400})

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the video to extract the best frame
        best_frame = extract_best_frame(file_path)

        if best_frame is not None:
            frame_path = os.path.join(RECOGNIZE_FOLDER, f'best_frame_{frame_counter}.jpg')
            print(f"Saving best frame to: {frame_path}")  # Debug statement
            success = cv2.imwrite(frame_path, best_frame)
            if not success:
                return jsonify({'msg': 'Failed to save the best frame', 'status': 500})

            frame_counter += 1
            results = compare_multiple_images(frame_path, FRAME_FOLDER)

            for filename, score in results:
                print(f"Image: {filename}, Similarity Score: {score:.2f}")

            return jsonify({'msg': 'Best frame extracted and saved', 'status': 200, 'frame_path': frame_path})
        else:
            return jsonify({'msg': 'Failed to extract best frame', 'status': 500})
    except Exception as e:
        return jsonify({'msg': str(e), 'status': 500})

def extract_best_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    best_frame = None
    best_score = -np.inf

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate a score for the frame (e.g., variance of pixel intensities)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Update the best frame if the current frame has a higher score
        if score > best_score:
            best_score = score
            best_frame = frame

    cap.release()
    return best_frame

def load_image(image_path):
    # Load an image using OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return image

def compare_images(image1, image2):
    # Compute SSIM between the two images
    score, _ = ssim(image1, image2, full=True)
    return score

def compare_multiple_images(reference_image_path, image_folder):
    # Load the reference image
    reference_image = load_image(reference_image_path)

    # Initialize a list to store results
    results = []

    # Iterate through all images in the folder
    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)
        if os.path.isfile(image_path):
            # Load the current image
            current_image = load_image(image_path)

            # Compare the current image with the reference image
            similarity_score = compare_images(reference_image, current_image)

            # Store the result
            results.append((filename, similarity_score))

    # Sort results by similarity score in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    return results

if __name__ == '__main__':
    app.run(debug=True)
