from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import os
from os.path import basename
from flask import Flask, request,redirect,jsonify,render_template
from flask_cors import CORS

app = Flask(__name__,static_folder='static',template_folder='template')
CORS(app)

static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')

app.config['UPLOAD_FOLDER'] = os.path.join(static_folder, 'Uploads')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sign.html')
def sign():
    return render_template('sign.html')

@app.route('/uploadfile.html', methods=["POST","GET"])
def upload_image():
    if request.method == 'POST':

        if 'image' not in request.files:
            return render_template('uploadfile.html')
    
        file = request.files['image']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            file.save(file_path)
        except FileNotFoundError as e:
            app.logger.error(f"File not found: {e}")
            return render_template('uploadfile.html',result_data="null"), 404

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
    
        np.set_printoptions(suppress=True)
    
        model = load_model("keras_Model.h5", compile=False)
    
        class_names = ["thushara","gotabaya","janith","lakshan","fake"]
    
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    
        image = Image.open(file_path).convert("RGB")
    
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    
        image_array = np.asarray(image)
    
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
        data[0] = normalized_image_array
    
        prediction = model.predict(data)
        print(prediction)
        index = np.argmax(prediction)
        class_name = class_names[index]

        errdata = {
            "verified":"unverified",
            "name":"-",
            "image_path": "Uploads/" + file.filename
        }

        cordata = {
            "verified":"verified",
            "name":class_name,
            "image_path": "Uploads/" + file.filename
        }

        if(index == len(class_names)-1):
            return render_template('uploadfile.html',result_data=errdata), 401

        return render_template('uploadfile.html',result_data=cordata), 200
    
    return render_template('uploadfile.html',result_data="null")
    
@app.route('/', methods=['POST'])
def save_image():
    try:
        image = request.files['image']
        image.save('path/to/your/saving/folder/drawing.png')
        return 'Image saved successfully.', 200
    except Exception as e:
        return f'Error: {str(e)}', 500
    
    upload_image()

if __name__ == "__main__":
    app.run(debug=True,port=5001)
