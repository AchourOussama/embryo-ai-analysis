from flask import Flask, Blueprint, request, jsonify,send_from_directory
from flask_cors import CORS, cross_origin

# from tensorflow.keras.models import load_model
import pandas
from werkzeug.utils import secure_filename

import os
from dotenv import load_dotenv

import numpy 
from PIL import Image

from model import predict , segment, load_classification_model
import threading


#Blob
from azure.storage.blob import BlobServiceClient

#SQL
import pyodbc, struct
from azure import identity
from typing import Union
# from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.json import pydantic_encoder


#for connecting with service principal
import msal
import adal

import json




#loading .env to environment
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
UPLOAD_FOLDER = './input_images'
SEGMENTED_IMAGES='./segmented-images'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEGMENTED_IMAGES'] = SEGMENTED_IMAGES


#Connection strings to SQL DB and Blob Storage
sql_connection_string = os.environ["AZURE_SQL_CONNECTION_STRING"]
blob_connection_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.environ["CONTAINER_NAME"]


model=load_classification_model()


class PredictedProbabilities(BaseModel):
    bad: float
    average: float
    good: float
    def __init__(self, bad: float, average: float, good:float, decimal_places: int = 2):
        super().__init__(bad=round(bad, decimal_places),
                        average=round(average, decimal_places),
                        good=round(good, decimal_places)
                        )

   
class ResultModel(BaseModel):
    predicted_class: str
    predicted_probabilities: PredictedProbabilities

class Embryo(BaseModel):

    # ImageUrl: Union[str, None] = None
    ImageName:str
    Result:ResultModel
    suggested_value:Union[str, None] = None
    note:Union[str, None] = None



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

            #saving image locally
            uploaded_file.save(destination_file)

            # #saving image in blob
            # saveToBlob(uploaded_file,destination_file)

            #processing the image : class prediction & segmentation
            predicted_probabilities={}
            predicted_class,predicted_probabilities=process_image(filename,destination_file)
            # print("predicted_class{}\npredicted_probabilities{}".format(predicted_class,predicted_probabilities))
            
            # loading the json object to extract data
            predicted_probabilities=json.loads(predicted_probabilities)

            predicted_probabilities=PredictedProbabilities(bad=predicted_probabilities['bad'],average=predicted_probabilities['average'],good=predicted_probabilities['good'])
            result=ResultModel(predicted_class=predicted_class,predicted_probabilities=predicted_probabilities)            
            
            #saving image in sql db
            embryo= Embryo(ImageName=filename,Result=result,suggested_value=None,note=None)
            
            #converting final result to json string 
            result=json.dumps(result,default=pydantic_encoder)
            print("final result",result)

            # Embed the result with the image URL
            image_with_result = {'image_name':filename , 'result': result}

            # Saving image in Blob and image results in SQL DB : These task run in background 
            print("thread begins")
            threading.Thread(target=saveToBlob, args=(uploaded_file, destination_file)).start()
            threading.Thread(target=saveToSQLDB, args=(embryo,predicted_probabilities)).start()

        

            return jsonify({'message': 'Image processed successfully', 'image_with_result': image_with_result}), 201
            # return jsonify({'message': 'Image processed successfully'}), 201

        else:
            return jsonify({'error': 'Invalid file type, only JPEG images are allowed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg','png', 'jpeg','bmp'}

# def load_model():


def process_image(image_name,image_path):
    
    #image segmentation
    segmented_image=segment(image_path)
    segmented_image_path = os.path.join(app.config['SEGMENTED_IMAGES'], image_name)
    #saving image locally
    # segmented_image.save(segmented_image_path)
    # segmented_image = segmented_image.astype(np.uint8)  # Convert the data to uint8 type

    # Convert the NumPy array to a Pillow image
    image_pil = Image.fromarray(segmented_image.astype(numpy.uint8))

    # Save the image
    image_pil.save(segmented_image_path)


    #class prediction
    percentages={}
    print("begin predict")

    predicted_probabilities=predict(model=model,image_path=image_path,image_name=image_name)
    print("end predict")

    # Load the results CSV file
    labeled_results_csv_file='./results/labeled_results_csv.csv'
    results_df = pandas.read_csv(labeled_results_csv_file)

    row = results_df.loc[results_df['image_name'] == image_name]
    print("row",row)
    predicted_class=row['classification'].to_string(index=False)
    # print(image_name)
    # print(result)
    print("predicted_class{}\npredicted_probabilities{}".format(predicted_class,predicted_probabilities))

    return predicted_class , predicted_probabilities


# Function to establish connection to blob storage
def get_blob_service_client():
    # retrieve the connection string from the environment variable
    return BlobServiceClient.from_connection_string(blob_connection_str)

# retrieve the container name (in which images will be store in the storage account)  from the environment variable
def saveToBlob(file,filepath):
    blob_service_client=get_blob_service_client()
    try:

        container_client = blob_service_client.get_container_client(container=container_name) # get container client to interact with the container in which images will be stored
        container_client.get_container_properties() # get properties of the container to force exception to be thrown if container does not exist
    except Exception as e:
        print(e)
        print("Creating container...")
        container_client = blob_service_client.create_container(container_name) # create a container in the storage account if it does not exist

    try:
        with open(file=filepath, mode="rb") as data:
            #deleting [ , ] symbols from file name 
            
            blob_client = container_client.upload_blob(name=remove_square_brackets(file.filename), data=data, overwrite=True)
            print("after blob")
    except Exception as e:
        print(e)
        print("Ignoring duplicate filenames") # ignore duplicate filenames

def remove_square_brackets(filename):
    # Replace square brackets with an empty string
    return filename.replace('[', '').replace(']', '')

def saveToSQLDB(item: Embryo,predicted_probabilities:PredictedProbabilities):
    print("********* saving data to DB .... ********* ")
    #Environments variables to have access to Blob Storage
    sas_token=os.environ["SAS_TOKEN"]
    storage_account_url=os.environ["STORAGE_ACCOUNT_URL"]

    try:
    
        # conn = get_conn()
        conn=connect_oauth()
        cursor = conn.cursor()

        # Table should be created ahead of time in production app.
        cursor.execute("""

            CREATE TABLE EmbryoResults (
                Id INT NOT NULL PRIMARY KEY IDENTITY,
                ImageName NVARCHAR(MAX),
                PredictedClass NVARCHAR(MAX),
                PredictedProbabilities NVARCHAR(MAX),
                SuggestedValue NVARCHAR(MAX) NULL,
                Note NVARCHAR(MAX) NULL
            );
        """)

        conn.commit()

        # conn.commit()
    except Exception as e:
        # Table may already exist
        print(e)

    print("******* Inserting new row ... *********")
    cursor.execute(f"INSERT INTO EmbryoResults (ImageName, PredictedClass,PredictedProbabilities,SuggestedValue,Note) VALUES (?,?,?,?,?)", item.ImageName, item.Result.predicted_class,json.dumps(predicted_probabilities,default=pydantic_encoder),item.suggested_value,item.note)
    # cursor.execute(f"INSERT INTO EmbryoResults (ImageName, PredictedClass,PredictedProbabilities,SuggestedValue,Note) VALUES (?,?,?,?,?)", item.ImageName, "good","hello",item.suggested_value,item.note)

    conn.commit()

    print("successfully added in sql db")
    return item

### connected with sql db in default way
def get_conn():
    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    print("********* connecting to sql db .... ********* ")
    conn = pyodbc.connect(sql_connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn

### connected with sql db using service principal 
def connect_oauth():
    tenant_id = os.environ.get('AZURE_TENANT_ID')
    clientId = os.environ.get('AZURE_CLIENT_ID')
    clientSecret = os.environ.get('AZURE_CLIENT_SECRET')
    server = os.environ.get('SQL_SERVER')
    database = os.environ.get('SQL_DATABASE')
    print(tenant_id,clientId,clientSecret,server,database)
    
    authorityHostUrl = "https://login.microsoftonline.com"
    authority_url = authorityHostUrl + "/" + tenant_id
    context = adal.AuthenticationContext(authority_url,   api_version=None)
    token = context.acquire_token_with_client_credentials("https://database.windows.net/", clientId, clientSecret)
    driver = "{ODBC Driver 18 for SQL Server}"
    #   conn_str = "DRIVER=" + driver + ";server=" + server + ";database="+ database
    conn_str=sql_connection_string
    print("connection string",conn_str)
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    tokenb = bytes(token["accessToken"], "UTF-8")
    exptoken = b''
    for i in tokenb:
        exptoken += bytes({i})
        exptoken += bytes(1)
    tokenstruct = struct.pack("=i", len(exptoken)) + exptoken
    conn = pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: tokenstruct})
    return conn

# Function to retrieve all blobs (images) from Azure Blob Storage
def list_blobs_in_container():
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return [blob.name for blob in blob_list]

# Function to retrieve results from Azure SQL Database
def get_all_results():
    print("from get image from sql db")

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ImageName, PredictedClass, PredictedProbabilities, SuggestedValue, Note FROM EmbryoResults")
    rows = cursor.fetchall()
    print("rows",rows)
    conn.close()
    # return {row.ImageName: row.Result for row in results}
    results = {}


    for row in rows:
        results[row.ImageName] = {
            'predicted_class': row.PredictedClass,
            'predicted_probabilities': row.PredictedProbabilities,
            'suggested_value': row.SuggestedValue,
            'note': row.Note
        }
    
    print("results",results)

    return results
# API endpoint to list all images and their results
@app.route('/images', methods=['GET'])
def list_images_and_results():
    try:
        # Retrieve all blobs (images) from Azure Blob Storage
        images = list_blobs_in_container()

        # Retrieve all results from Azure SQL Database
        results = get_all_results()

        # Combine the data
        response = []

        for image in images:
            result_data = results.get(image, {
                'predicted_class': "No result found",
                'predicted_probabilities': "No result found",
                'suggested_value': None,
                'note': None
                })
            # image_name=result_data['image_name']
            response.append({
                "image_name": image,
                "image_path": f"http://localhost:5000/images/{image}",
                "segmented_image_path":f"http://localhost:5000/segmented-images/{image}",
                "predicted_class": result_data['predicted_class'],
                "predicted_probabilities": result_data['predicted_probabilities'],
                "suggested_value": result_data['suggested_value'],
                "note": result_data['note']
            })

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/segmented-images/<path:filename>')
def get_segmented_image(filename):
    return send_from_directory(SEGMENTED_IMAGES, filename)

@app.route('/update', methods=['POST'])
def update_embryo():
    data = request.json
    print(data)
    image_name=data['image_name']
    predicted_class=data['predicted_class']
    predicted_probabilities=data['predicted_probabilities']
    suggested_value = data['suggested_value']
    note = data['note']
    try:
        conn = connect_oauth()
        cursor = conn.cursor()

        # Check if the embryo exists
        cursor.execute("SELECT * FROM EmbryoResults WHERE ImageName = ?", (image_name,))
        embryo = cursor.fetchone()

        if not embryo:
            return jsonify({'error': 'Embryo not found'}), 404

    # Update the embryo with new values
        cursor.execute("""
            UPDATE EmbryoResults
            SET PredictedClass = ?, PredictedProbabilities = ?, SuggestedValue = ?, Note = ?
            WHERE ImageName = ?""", (predicted_class, predicted_probabilities, suggested_value, note, image_name)
             
            )


        conn.commit()
        conn.close()

        return jsonify({'message': 'Embryo updated successfully'}), 200

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({'error': str(e)}), 500

  


###  THIS DOESN'T WORK !! :   API endpoint to retrieve image and result

# Function to retrieve image from Azure Blob Storage
def get_image_from_blob(image_name):
    print("from get image from blob")
    blob_client = get_blob_service_client().get_blob_client(container=container_name, blob=image_name)
    image_data = blob_client.download_blob().readall()
    return image_data

# Function to retrieve result from Azure SQL Database
def get_result_from_db(image_name):
    print("from get image from sql db")

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT Result FROM EmbryoResults WHERE ImageName = ?", image_name)
    result = cursor.fetchone()[0]  # Assuming result is in the first column
    conn.close()
    return result

@app.route('/image/<image_name>', methods=['GET'])
def get_image_and_result(image_name):
    print("from get_image_and_result method ")
    print(image_name)
    try:
        # Retrieve image from Azure Blob Storage
        image_data = get_image_from_blob(image_name)

        # Retrieve result from Azure SQL Database
        result = get_result_from_db(image_name)

        # Return image and result as JSON response
        response = {
            "image_name": image_name,
            "image_data": image_data,
            "result": result
        }
        return jsonify({'message': 'Image retrieved successfully', 'response':response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# This is are unused APIs

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
