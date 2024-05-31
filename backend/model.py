from tensorflow.keras.models import load_model
import numpy as np
import os
from tqdm import tqdm
import cv2
from albumentations import CLAHE

import pandas 

def predict():
    # Folder containing test images
    test_image_folder = './input_images/'

    # Get a list of file names in the test image folder
    test_image_names = os.listdir(test_image_folder)

    # Preprocess test images
    test_images = []
    for image_name in tqdm(test_image_names):
        # Concatenate image folder path with file name
        image_path = os.path.join(test_image_folder, image_name)

        # Check if the file is an image
        if not image_name.endswith(('.BMP', '.jpeg', '.png', '.bmp', '.gif')):
            print(f"Skipping non-image file: {image_name}")
            continue

        # Read the image
        image = cv2.imread(image_path)

        # Check if the image was read successfully
        if image is None:
            print(f"Error reading image: {image_path}")
            continue

        # Apply CLAHE to each channel of the image
        clahe = CLAHE(clip_limit=2.0, tile_grid_size=(1, 1))
        enhanced_image = clahe(image=image)['image']

        # Resize the image to the same size as training images (299x299)
        resized_image = cv2.resize(enhanced_image, (299, 299))

        # Normalize the pixel values to the range [0, 1]
        normalized_image = resized_image.astype(np.float32) / 255.0

        # Add the preprocessed image to the list
        test_images.append(normalized_image)

    # Convert the list of images to a numpy array
    test_images = np.array(test_images)


    #loading the model
    MODEL_PATH="./models/Images_checkpoint.h5"
    # INPUT_PATH="./input_images/MTL-0130-1652-5E96-P09-FP4.jpg_0_0.bmp"
    model = load_model(MODEL_PATH)
    model.summary()
    predictions=model.predict(test_images)

    # Get predicted classes
    predicted_classes = np.argmax(predictions, axis=1)


    # Create a DataFrame with image names and predictions
    results_df = pandas.DataFrame({'image_name': test_image_names, 'classification': predicted_classes})

    # Save the DataFrame to a CSV file
    results_csv_file = './results/results_csv.csv'
    results_df.to_csv(results_csv_file, index=False)
    print("Predictions saved to:", results_csv_file)


    # Load the results CSV file
    results_df = pandas.read_csv(results_csv_file)

    # Replace numeric classifications with labels
    classification_labels = {1: 'good', 2: 'average', 3: 'bad'}
    # print(results_df['classification'])
    # print(results_df['classification'].to_string(index=False))
    
    results_df['classification'] = results_df['classification'].map(classification_labels)

    # Save the updated DataFrame to a new CSV file
    labled_results_csv_file = './results/labled_results_csv.csv'
    results_df.to_csv(labled_results_csv_file, index=False)
    print("Labled predictions saved to:", labled_results_csv_file)



predict()