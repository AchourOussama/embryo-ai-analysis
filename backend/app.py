from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS, cross_origin

from model import predict
from tensorflow.keras.models import load_model
import pandas
from werkzeug.utils import secure_filename

import os
from dotenv import load_dotenv
#Blob
from azure.storage.blob import BlobServiceClient

#SQL 
import pyodbc, struct
from azure import identity
from typing import Union
# from fastapi import FastAPI
from pydantic import BaseModel

#loading .env to environment
load_dotenv()

app = Flask(__name__)
cors = CORS(app)
UPLOAD_FOLDER = './input_images'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Connecting to Bolb 

#Connecting to SQL DB
connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]
print("*********connection_string:\n",connection_string)


class Embryo(BaseModel):
    
    # ImageUrl: Union[str, None] = None
    ImageName:str
    Result: str


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

            #saving image in blob 
            saveToBlob(uploaded_file,destination_file)

            #processing the image 
            result = process_image(filename)

            #saving image in sql db 
            embryo= Embryo(ImageName=filename,Result=result)
            saveToSQLDB(embryo)



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

def saveToBlob(file,filepath):
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING') # retrieve the connection string from the environment variable
    container_name = "pictures" # container name in which images will be store in the storage account

    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str) # create a blob service client to interact with the storage account
    try:
        container_client = blob_service_client.get_container_client(container=container_name) # get container client to interact with the container in which images will be stored
        container_client.get_container_properties() # get properties of the container to force exception to be thrown if container does not exist
    except Exception as e:
        print(e)
        print("Creating container...")
        container_client = blob_service_client.create_container(container_name) # create a container in the storage account if it does not exist
    
    try:
        with open(file=filepath, mode="rb") as data:
            print("before blob")
            blob_client = container_client.upload_blob(name=file.filename, data=data, overwrite=True)
            print("after blob")
    except Exception as e:
        print(e)
        print("Ignoring duplicate filenames") # ignore duplicate filenames


def saveToSQLDB(item: Embryo):
    print("********* saving data to DB .... ********* ")
    sas_token=os.environ["SAS_TOKEN"]
    storage_account_url=os.environ["STORAGE_ACCOUNT_URL"]

    try:
        conn = get_conn()
        cursor = conn.cursor()
        storage_account_url=""

        # Table should be created ahead of time in production app.
        cursor.execute("""

            CREATE TABLE EmbryoResults (
                Id INT NOT NULL PRIMARY KEY IDENTITY,
                ImageName NVARCHAR(MAX), 
                Result NVARCHAR(MAX)
            );
        """)
        
        conn.commit()

        # This is two sql queries are for retrieving image url and storing it in DB

        # #creating external Azure Blob data source 
        # cursor.execute("""
        #     CREATE DATABASE SCOPED CREDENTIAL sampleblobcred1
        #         WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
        #         SECRET = ?;
        # """,(sas_token,))
        
        # conn.commit()


        # cursor.execute("""
        #     CREATE EXTERNAL DATA SOURCE blobstorage
        #     WITH (
        #         TYPE = BLOB_STORAGE,
        #         LOCATION = ?,
        #         CREDENTIAL = sampleblobcred1);
        #     """, (storage_account_url,))
        
        

        # conn.commit()
    except Exception as e:
        # Table may already exist
        print(e)

    print("******* Inserting new row ... *********")
    cursor.execute(f"INSERT INTO EmbryoResults (ImageName, Result) VALUES (?, ?)", item.ImageName, item.Result)
    
    # Insert image url into table from blob storage using parameterized query

    # bulk="pictures/{}".format(item.ImageName)
    # print("bulk",bulk)
    # cursor.execute(f"INSERT INTO EmbryoResults (ImageUrl, ImageName, Result) VALUES ((SELECT BulkColumn FROM OPENROWSET(BULK ?,DATA_SOURCE = 'bolobstorage', SINGLE_BLOB) AS ImageFile), ?,?)", bulk, item.ImageName , item.Result)
    # sql = """
    # INSERT INTO EmbryoResults (ImageUrl) 
    # VALUES (
    #     (SELECT * FROM OPENROWSET(
    #         BULK 'pictures/personal.jpeg', 
    #         DATA_SOURCE = 'blobstorage', 
    #         SINGLE_BLOB
    #         ) AS ImageFile)
        
    # )
    # """
    # cursor.execute(sql)

    conn.commit()


    
    return item
def get_conn():
    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    print("********* connecting to sql db .... ********* ")
    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn



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

# image_name='MTL-0130-1652-5E96-P09-FP4.jpg_0_0.bmp'
# print('result:',process_image(image_name))

if __name__ == '__main__':
    app.run(debug=True)
