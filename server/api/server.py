import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import yolov5
import os   
import requests
import io
from flask_oauthlib.client import OAuth
from flask import Flask, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize OAuth objectz
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='your_consumer_key',
    consumer_secret='your_consumer_secret',
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/photoslibrary.readonly'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

yolo_model = yolov5.load('yolov5s.pt')
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
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    # Redirect to the home page after successful login
    return redirect(url_for('index'))

@app.route('/check_login')
def check_login():
    if 'google_token' in session:
        return jsonify({'status': 'loggedin'})
    else:
        return jsonify({'status': 'loggedout'})
    
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

# Retrieve user's photos from Google Photos API
def retrieve_user_photos():
    access_token = session.get('google_token')[0]
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

def detect_objects(image_path, model):
    image = Image.open(image_path).convert('RGB')
    results = model(image)
    predictions = results.pred[0]
    boxes = predictions[:, :4] 
    scores = predictions[:, 4]
    categories = predictions[:, 5]
    
    # Retrieve class names from the model
    class_names = model.module.names if hasattr(model, 'module') else model.names
    
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

@app.route('/')
def index():
    photos = retrieve_user_photos()
    for photo in photos:
        image_url = photo['baseUrl']
        features = extract_features(image_url)
        objects = detect_objects(image_url)
        if features is not None:
            print("Features extracted for photo:", photo['filename'])
    return 'Processing complete'

if __name__ == '__main__':
    app.run(debug=True)
