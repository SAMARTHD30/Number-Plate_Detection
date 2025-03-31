from flask import Flask, request, send_file, render_template_string, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import io
import torch
import torch.nn as nn
from ultralytics.nn.tasks import DetectionModel
from torch.nn import Sequential
from ultralytics.nn.modules.conv import Conv, Concat
from ultralytics.nn.modules.block import C2f, Bottleneck, SPPF
from ultralytics.nn.modules import *
from torch.nn.modules.upsampling import Upsample
from contextlib import contextmanager
from flask_cors import CORS
import logging
from flask_limiter import Limiter

# Define only the essential classes needed for YOLO
TRUSTED_CLASSES = [
    DetectionModel,
    Sequential,
    Conv,
    C2f,
    Bottleneck,
    SPPF,
    DFL,
    Proto,
    Concat,
    Upsample,
    nn.Conv2d,
    nn.BatchNorm2d,
    nn.SiLU,
    nn.Module,
    nn.ModuleList,
    nn.Upsample
]

@contextmanager
def allow_unsafe_load():
    original_load = torch.load
    def unsafe_load(*args, **kwargs):
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = unsafe_load
    try:
        yield
    finally:
        torch.load = original_load

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

limiter = Limiter(app, key_func=get_remote_address)

# Load the YOLO model
def load_yolo_model(model_path):
    try:
        with allow_unsafe_load():
            model = YOLO(model_path, task='detect')
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

# Load the model
model = load_yolo_model("best.pt")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running"})

@app.route("/detect", methods=["POST"])
def detect():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_bytes = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    # Run the model
    results = model(image)
    boxes = results[0].boxes.xyxy.cpu().numpy()

    if len(boxes) == 0:
        return jsonify({"message": "No license plate detected"}), 200

    # Prepare the response
    response_data = []
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        response_data.append({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })

    return jsonify({"detections": response_data}), 200

@app.route("/process", methods=["POST"])
def process_image():
    try:
        # Get the uploaded car image and custom content
        car_file = request.files["car_image"]
        custom_file = request.files.get("custom_image")  # Optional custom image
        custom_text = request.form.get("custom_text")    # Optional text

        # Load the car image
        car_img = cv2.imdecode(np.frombuffer(car_file.read(), np.uint8), cv2.IMREAD_COLOR)
        if car_img is None:
            return "Invalid image file", 400

        # Detect the license plate
        results = model(car_img)
        boxes = results[0].boxes.xyxy.cpu().numpy()

        if len(boxes) > 0:  # If a license plate is detected
            x1, y1, x2, y2 = map(int, boxes[0])  # Use the first detected plate
            w, h = x2 - x1, y2 - y1  # Calculate width and height

            # Replace with custom content
            if custom_file:  # If a custom image is provided
                custom_img = cv2.imdecode(np.frombuffer(custom_file.read(), np.uint8), cv2.IMREAD_COLOR)
                if custom_img is None:
                    return "Invalid custom image file", 400
                custom_img = cv2.resize(custom_img, (w, h))  # Resize to fit the plate
                car_img[y1:y2, x1:x2] = custom_img  # Overlay the custom image
            elif custom_text:  # If custom text is provided
                # Create a white background for the text
                car_img[y1:y2, x1:x2] = (255, 255, 255)
                font_scale = min(w, h) / 50  # Adjust font size based on plate size
                # Calculate text position to center it
                text_size = cv2.getTextSize(custom_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                text_x = x1 + (w - text_size[0]) // 2
                text_y = y1 + (h + text_size[1]) // 2
                cv2.putText(car_img, custom_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                           font_scale, (0, 0, 0), 2, cv2.LINE_AA)  # Black text

            # Convert the image to bytes and return it
            _, buffer = cv2.imencode(".jpg", car_img)
            return send_file(io.BytesIO(buffer), mimetype="image/jpeg")
        else:
            return "No license plate detected in the image. Please try with a clearer image of the license plate.", 400
    except Exception as e:
        return f"Error processing image: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)