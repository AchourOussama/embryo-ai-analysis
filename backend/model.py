import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import os
from tqdm import tqdm
import cv2
from albumentations import CLAHE
import json
from pydantic.json import pydantic_encoder
from PIL import Image
import matplotlib.pyplot as plt


import pandas 


def load_classification_model():
    print("################ Loading Classification Model ################")
    #loading the model
    MODEL_PATH="./models/Images_checkpoint.h5"
    # INPUT_PATH="./input_images/MTL-0130-1652-5E96-P09-FP4.jpg_0_0.bmp"
    model = load_model(MODEL_PATH)
    model.summary()
    return model

def predict(model,image_path,image_name):
    # Folder containing test images
    test_image_folder = './input_images/'

    # Get a list of file names in the test image folder
    # test_image_names = os.listdir(test_image_folder)

    # Preprocess test images
    images = []
    
    if not image_path.endswith(('.BMP', '.jpeg', '.png', '.bmp', '.jpg', '.gif')):
        print(f"File extension not compatible: {image_path}")
        raise Exception("File extension not compatible")

    # Read the image
    image = cv2.imread(image_path)

    # Check if the image was read successfully
    if image is None:
        print(f"Error reading image: {image_path}")
        raise Exception("Error reading image")


    # Apply CLAHE to each channel of the image
    clahe = CLAHE(clip_limit=2.0, tile_grid_size=(1, 1))
    enhanced_image = clahe(image=image)['image']

    # Resize the image to the same size as training images (299x299)
    resized_image = cv2.resize(enhanced_image, (299, 299))

    # Normalize the pixel values to the range [0, 1]
    normalized_image = resized_image.astype(np.float32) / 255.0

    # Add the preprocessed image to the list
    images.append(normalized_image)

    # Convert the list of images to a numpy array
    images = np.array(images)


    # #loading the model
    # MODEL_PATH="./models/Images_checkpoint.h5"
    # # INPUT_PATH="./input_images/MTL-0130-1652-5E96-P09-FP4.jpg_0_0.bmp"
    # model = load_model(MODEL_PATH)
    # model.summary()

    print("before predict from predict")
    predictions=model.predict(images)
    print(predictions)
    print("after predict from predict")

    #pourcentages 
    pourcentages={}
    pourcentages={
        "bad":predictions[0][0]*100,
        "average":predictions[0][2]*100,
        "good":predictions[0][1]*100

    }
    # Get predicted classes
    predicted_classes = np.argmax(predictions, axis=1)

    pourcentages = json.dumps(pourcentages,default=pydantic_encoder)

    # print("******** pourcentages: ",pourcentages)


    
    # # Save the DataFrame to a CSV file
    results_csv_file = './results/results_csv.csv'
    results_df = pandas.DataFrame({'image_name': image_name, 'classification': predicted_classes})

    if os.path.isfile(results_csv_file):
        # Read the existing CSV file
        existing_df = pandas.read_csv(results_csv_file)
        
        # Check if the image name already exists
        if image_name in existing_df['image_name'].values:
            print(f"Image name {image_name} already exists in the CSV file. Skipping append.")
        else:
            # Append the new DataFrame to the existing CSV file
            results_df.to_csv(results_csv_file, mode='a', header=False, index=False)
            print(f"Appended {image_name} to the CSV file.")
    else:
        # If the file does not exist, write the DataFrame with the header
        results_df.to_csv(results_csv_file, index=False)
        print(f"Created new CSV file and added {image_name}.")


    # Save the updated DataFrame to a new CSV file
    # Replace numeric classifications with labels
    classification_labels = {1: 'good', 2: 'average', 3: 'bad'}
    results_df['classification'] = results_df['classification'].map(classification_labels)

    labeled_results_csv_file = './results/labeled_results_csv.csv'
    if os.path.isfile(labeled_results_csv_file):
        # Read the existing CSV file
        existing_labeled_df = pandas.read_csv(labeled_results_csv_file)
        
        # Check if the image name already exists
        if image_name in existing_labeled_df['image_name'].values:
            print(f"Image name {image_name} already exists in the labeled CSV file. Skipping append.")
        else:
            # Append the new DataFrame to the existing CSV file
            # results_df = pandas.DataFrame({'image_name': image_name, 'classification': predicted_classes})
            results_df.to_csv(labeled_results_csv_file, mode='a', header=False, index=False)
            print(f"Appended {image_name} to the labeled CSV file.")
    else:
        # If the file does not exist, write the DataFrame with the header
        results_df.to_csv(results_csv_file, index=False)
        print(f"Created new labeled CSV file and added {image_name}.")
    # results_df.to_csv(labled_results_csv_file,mode='a', header=False, index=False)
    # print("Labled predictions saved to:", labled_results_csv_file)
    return pourcentages


# predict()

def segment(image_path):
    ## This decorators ensures that Keras knows how to serialize and deserialize the function when saving and loading the model.
    # @tf.keras.utils.register_keras_serializable()
    def iou(y_true, y_pred):
        def f(y_true, y_pred):
            intersection = (y_true * y_pred).sum()
            union = y_true.sum() + y_pred.sum() - intersection
            x = (intersection + 1e-15) / (union + 1e-15)
            x = x.astype(np.float32)
            return x
        return tf.numpy_function(f, [y_true, y_pred], tf.float32)

    smooth = 1e-15

    @tf.keras.utils.register_keras_serializable()
    def dice_coef(y_true, y_pred):
        y_true = tf.keras.layers.Flatten()(y_true)
        y_pred = tf.keras.layers.Flatten()(y_pred)
        intersection = tf.reduce_sum(y_true * y_pred)
        return (2. * intersection + smooth) / (tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + smooth)

    def dice_loss(y_true, y_pred):
        return 1.0 - dice_coef(y_true, y_pred)

    ##loading the model 
    SEGMENTATION_MODEL="./models/model_unet.h5"
    model = load_model(SEGMENTATION_MODEL, custom_objects={'iou': iou, 'dice_coef': dice_coef})

    ##segment image
    image = Image.open(image_path)
    plt.imshow(image)
    # plt.show()
    # Resize the image to match the expected input shape of the model
    image = np.array(image)

    x = cv2.resize(image, (256, 256))

    # Normalize the image
    # x=image
    x = x / 255.0
    x = x.astype(np.float32)

    # Perform prediction
    p = model.predict(np.expand_dims(x, axis=0))[0]
    print("segmentation successful")
    # Convert prediction to mask
    p = np.argmax(p, axis=-1)
    p = np.expand_dims(p, axis=-1)
    p = p * (255 / 6)
    p = p.astype(np.int32)
    p = np.concatenate([p, p, p], axis=2)

    print("image successfully segmented")
    return p



