import io
import os
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from base64 import encodebytes
from PIL import Image
from log import RequestLogger, ServerLoadLogger
from plot import get_exercises, get_info, plot_all

load_dotenv()

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}})

request_logger = RequestLogger()
load_logger = ServerLoadLogger()

with app.app_context():
    load_logger.start_logging()
    request_logger.log_request(request)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

root = os.path.dirname(__file__)

@app.route('/', methods=["GET", "POST", "OPTION"])
def default():
    return jsonify('OK'), 200

@app.route('/get_gainz', methods=["POST"])
def get_gainz():
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files.get('file')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if len(file.read()) > MAX_FILE_SIZE_BYTES:
        return jsonify({'error': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes'}), 400
    
    exercises_info = get_info(os.path.join(root, "exercises.csv"))
    try:
        exercises = get_exercises(file, '%Y-%m-%d %H:%M:%S', exercises_info)
    except ValueError as e:
        return jsonify({'error': e}), 400
    
    plot_all(exercises, os.path.join(root, "./plots/"))

    encoded_images = []
    for _, _, files in os.walk(os.path.join(root, "./plots")):
        for file_name in files:
            encoded_images.append(_get_response_image(os.path.join(root, "./plots/" + file_name)))
            os.remove(os.path.join(root, "./plots/" + file_name))
    response = jsonify(encoded_images)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def _get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img