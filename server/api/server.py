import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
from ultralytics import YOLO
import os   
import requests
import io
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, session
from flask import send_from_directory, jsonify
from flask_cors import cross_origin, CORS
from dotenv import dotenv_values

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'your_secret_key'

# Initialize OAuth object
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=dotenv_values['GOOGLE_CLIENT_ID'],
    client_secret=dotenv_values['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    redirect_uri='http://localhost:5000/auth/google/callback',
    client_kwargs={'scope': 'openid profile email https://www.googleapis.com/auth/photoslibrary.readonly'}
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

@app.route('/login')
@cross_origin()
def login():
    return google.authorize_redirect(redirect_uri=url_for('auth', _external=True))

@app.route('/auth/google/callback')
@cross_origin()
def auth():
    token = google.authorize_access_token()
    session['google_token'] = token
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def detect_objects(image_path):
    image = Image.open(image_path).convert('RGB')
    results = yolo_model(image)
    predictions = results.pred[0]
    boxes = predictions[:, :4] 
    scores = predictions[:, 4]
    categories = predictions[:, 5]
    
    # Retrieve class names from the model
    class_names = yolo_model.names
    
    # Iterate over each detected object and print its name
    for box, score, category in zip(boxes, scores, categories):
        class_index = int(category)
        class_name = class_names[class_index]
        print("Bounding Box:", box, "Score:", score, "Class:", class_name)
    
    results.show()
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
        print("Error retrieving user's photos:", response.status_code)
        return []

@app.route('/')
def index():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    # Retrieve user's photos from Google Photos API
    photos = retrieve_user_photos()
    for photo in photos:
        image_url = photo['baseUrl']
        # Uncomment the following line if you want to detect objects in the photos
        # objects = detect_objects(image_url)
        features = extract_features(image_url)
        if features is not None:
            print("Features extracted for photo:", photo['filename'])
    return 'Processing complete'

@app.route('/check_login')
def check_login():
    if 'google_token' in session:
        return jsonify({'isLoggedIn': True})
    else:
        return jsonify({'isLoggedIn': False})
    
if __name__ == '__main__':
    app.run(debug=True)