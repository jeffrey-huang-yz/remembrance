import torch
import torchvision.models as models
import torchvision.transforms as transforms
import requests
from PIL import Image
from io import BytesIO
import numpy as np
from ultralytics import YOLO
import os   
import io
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session
from flask import send_from_directory, jsonify
from flask_cors import cross_origin, CORS
from dotenv import load_dotenv
from pymongo import MongoClient


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'your_secret_key'

#MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['user-photos']

def insert_data(photo_link, user_id, objects, features):
    collection = db['user-photos']
    data = {
        'photo_link': photo_link,
        'user_id': user_id,
        'objects': objects,
        'features': features
    }
    collection.insert_one(data)

def check_image_existence(photo_link):
    collection = db['user-photos']
    # Query the database to check if the photo exists already
    result = collection.find_one({'photo_link': photo_link})
    return result is not None

# Initialize OAuth object
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    redirect_uri='http://localhost:5000/auth/google/callback',
    client_kwargs={'scope': 'openid profile email https://www.googleapis.com/auth/photoslibrary.readonly'
    },
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs",

)


yolo_model = YOLO('yolov8s.pt')
yolo_model.conf = 0.25  # NMS confidence threshold
yolo_model.iou = 0.45  # NMS IoU threshold
yolo_model.agnostic = False  # NMS class-agnostic
yolo_model.multi_label = False  # NMS multiple labels per box
yolo_model.max_det = 1000  # maximum number of detections per image

# ResNet model loading
resnet_model = models.resnet18(pretrained=True)
resnet_model = torch.nn.Sequential(*(list(resnet_model.children())[:-1]))
preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


@app.route('/login', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@cross_origin(supports_credentials=True, )
def login():
    return google.authorize_redirect(redirect_uri=url_for('auth', _external=True))

@app.route('/auth/google/callback')
@cross_origin()
def auth():
    token = google.authorize_access_token()
    session['google_token'] = token
    return redirect('http://localhost:3000/home')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def detect_objects(image_path):
    response = requests.get(image_path)
    image = Image.open(BytesIO(response.content)).convert('RGB')
    results = yolo_model(image)
    print(results)
    for result in results:
        boxes = result.boxes  # Boxes object for bounding box outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs\
        
        result.show()  # display to screen
    
    # Retrieve class names from the model
    class_names = yolo_model.names
    
    # Iterate over each detected object and print its name
    for box, score, category in zip(boxes, scores, categories):
        class_index = int(category)
        class_name = class_names[class_index]
        print("Bounding Box:", box, "Score:", score, "Class:", class_name)
    
    print() 
    return boxes, scores, categories

def extract_features(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        image_tensor = preprocess(image)
        image_tensor = image_tensor.unsqueeze(0)
        with torch.no_grad():
            features = resnet_model(image_tensor)
        return features.squeeze().numpy()
    else:
        print("Error downloading image:", response.status_code)
        return None

def retrieve_user_photos():
    access_token = session.get('google_token')['access_token']
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Accept': 'application/json'
    }
    api_url = 'https://photoslibrary.googleapis.com/v1/mediaItems'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return response.json().get('mediaItems', [])
    else:
        raise Exception(f"Error retrieving user's photos: {response.status_code}")


@app.route('/update-photos')
def update_photos():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    # Retrieve user's photos from Google Photos API
    photos = retrieve_user_photos()
    for photo in photos:
        image_url = photo['baseUrl']
        print("Processing photo:", photo['filename'])
        
        # Check if the image URL already exists in the database
        if not check_image_existence(image_url):
            objects = detect_objects(image_url)
            features = extract_features(image_url)
            if features is not None:
                print("Features extracted for photo:", photo['filename'])
                # Insert data into MongoDB
                insert_data(image_url, session.get('google_token')['user_id'], objects, features)
        else:
            print("Skipping photo - Already exists in the database")

    return 'Processing complete'

@app.route('/check-login')
def check_login():
    if 'google_token' in session:
        return jsonify({'isLoggedIn': True})
    else:
        return jsonify({'isLoggedIn': False})
    
if __name__ == '__main__':
    app.run(debug=True)