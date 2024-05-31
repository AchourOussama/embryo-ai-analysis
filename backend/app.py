from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
# from keras.models import load_model
from tensorflow.keras.models import load_model
import os
from model import predict
import pandas


app = Flask(__name__)
cors = CORS(app)
UPLOAD_FOLDER = './input_images'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#loading the model
# MODEL_PATH="./models/Images_checkpoint.h5"
# INPUT_PATH="./input_images/MTL-0130-1652-5E96-P09-FP4.jpg_0_0.bmp"
# model = load_model(MODEL_PATH)
# model.summary()

# prediction=model.predict()

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
            result = process_image(filename)

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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','png', 'jpeg','bmp'}

def process_image(image_name):
    predict()
    # Load the results CSV file
    labled_results_csv_file='./results/labled_results_csv.csv'
    results_df = pandas.read_csv(labled_results_csv_file)

    row = results_df.loc[results_df['image_name'] == image_name]
    result=row['classification'].to_string(index=False)
    print(image_name)
    print(result)
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

image_name='MTL-0130-1652-5E96-P09-FP4.jpg_0_0.bmp'
print('result:',process_image(image_name))

if __name__ == '__main__':
    app.run(debug=True)
