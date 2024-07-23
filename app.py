from flask import Flask, request, send_from_directory, send_file
from flask_restful import Api, Resource
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from rembg import remove 
import io
from PIL import Image
import os

app = Flask(__name__)

CORS(app)
api = Api(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def load_and_preprocess_image(filepath):
  img = cv2.imread(filepath)  # Leer la imagen con OpenCV
  img = remove(img) # Eliminamos el fondo
  img = cv2.resize(img, (250, 250))  # Redimensionar la imagen
  #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Convertimos a grises
  img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertir de BGR a RGB
  img = img.astype('float32') / 255.0  # Normalizar la imagen
  return img

class imagen(Resource):
    def post(self):
        imagen_path = request.files['imagen_path'] # Obtener el archivo de imagen enviado en la solicitud
        if imagen_path and allowed_file(imagen_path.filename):
            # Guardar el archivo de imagen en el directorio de uploads
            filename = secure_filename(imagen_path.filename)
            imagen_path.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #retorno la imagen
            # Procesar la imagen
            img = load_and_preprocess_image(f'uploads/{filename}')

            # Convertir la imagen a un formato que se pueda enviar
            img = (img * 255).astype(np.uint8)  # Desnormalizar la imagen
            img = Image.fromarray(img)
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=70)
            img_io.seek(0)

            return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='processed_image.jpg')
            
        else:
            return {"message": "Invalid file or file extension not allowed"}, 400

api.add_resource(imagen, '/imagen')
