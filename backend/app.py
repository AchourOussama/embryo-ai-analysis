from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
cors = CORS(app)
UPLOAD_FOLDER = './output/'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/')
def index():
    print("Hello, World!")
    return "Hello, World!"

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        uploaded_file = request.files['image']
        if uploaded_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            destination_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(destination_file)

            #processing the image 
            result = process_image(destination_file)

            # Embed the result with the image URL
            image_with_result = {'image':destination_file , 'result': result}
            # This are returns for just the upload
            #     return jsonify({'message': 'File uploaded successfully', 'file': filename}), 201
            # else:
            #     return jsonify({'error': 'Invalid file type, only JPEG images are allowed'}), 400

            return jsonify({'message': 'Image processed successfully', 'image_with_result': image_with_result}), 201
        else:
            return jsonify({'error': 'Invalid file type, only JPEG images are allowed'}), 400


    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','png', 'jpeg'}

def process_image(image_path):
    # Replace this with your actual machine learning model code
    # For demonstration purposes, let's just return a dummy result

    #dummy values
    result = "poor"
    return result


@app.route('/get', methods=['GET'])
def list():
    print("getting data from flask")
    data={'message':'getting data from flask'}
    return jsonify(data)

#for testing
@app.route('/data')
def get_data():
    data = {'message': 'This is data from the Flask API'}
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
