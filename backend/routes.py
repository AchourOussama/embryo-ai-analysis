# app/routes.py
from flask import Blueprint, request, jsonify

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hello, World!"

@main.route('/upload', methods=['POST'])
def upload_image():
    # This is where you will handle image uploads
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))
        return jsonify({'message': 'File uploaded successfully'}), 201
    return jsonify({'message': 'No file uploaded'}), 400
