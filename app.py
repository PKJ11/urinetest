from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['urine_strip_db']
collection = db['colors']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    image_np = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    colors = extract_colors(img)

    collection.insert_one({'colors': colors})

    return jsonify({'colors': colors})

def extract_colors(img):
    img = cv2.resize(img, (300, 300))
    height, width, _ = img.shape
    strip_height = height // 10

    colors = []
    for i in range(10):
        strip = img[i * strip_height:(i + 1) * strip_height, :]
        avg_color = cv2.mean(strip)[:3]
        colors.append(tuple(map(int, avg_color)))

    return colors

if __name__ == '__main__':
    app.run(debug=True)
