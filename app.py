from flask import Flask, request, send_file, render_template_string
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
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>License Plate Editor</title>
        <style>
            :root {
                --primary: #2563eb;
                --error: #dc2626;
                --bg: #f8fafc;
                --text: #1e293b;
            }
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: system-ui, -apple-system, sans-serif;
                line-height: 1.5;
                color: var(--text);
                background: var(--bg);
                max-width: 600px;
                margin: 0 auto;
                padding: 1rem;
            }
            h1 {
                font-size: 1.5rem;
                margin: 1rem 0;
                text-align: center;
            }
            form {
                display: grid;
                gap: 1rem;
                background: white;
                padding: 1.5rem;
                border-radius: 0.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .input-group {
                display: grid;
                gap: 0.5rem;
            }
            label {
                font-weight: 500;
                font-size: 0.875rem;
            }
            input {
                width: 100%;
                padding: 0.5rem;
                border: 1px solid #e2e8f0;
                border-radius: 0.375rem;
                font-size: 0.875rem;
            }
            button {
                background: var(--primary);
                color: white;
                border: none;
                padding: 0.75rem 1rem;
                border-radius: 0.375rem;
                font-weight: 500;
                cursor: pointer;
                transition: opacity 0.15s;
            }
            button:hover {
                opacity: 0.9;
            }
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            #result {
                margin-top: 1.5rem;
                text-align: center;
            }
            #resultImage {
                max-width: 100%;
                border-radius: 0.375rem;
                display: none;
            }
            .error {
                color: var(--error);
                font-size: 0.875rem;
                margin-top: 0.5rem;
                display: none;
            }
            .loading {
                display: none;
                justify-content: center;
                align-items: center;
                gap: 0.5rem;
                color: var(--text);
                font-size: 0.875rem;
            }
            .spinner {
                width: 1rem;
                height: 1rem;
                border: 2px solid #e2e8f0;
                border-top-color: var(--primary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <h1>License Plate Editor</h1>
        <form id="uploadForm">
            <div class="input-group">
                <label for="car_image">Car Image</label>
                <input type="file" id="car_image" name="car_image" accept="image/*" required>
            </div>

            <div class="input-group">
                <label for="custom_image">Custom Image (optional)</label>
                <input type="file" id="custom_image" name="custom_image" accept="image/*">
            </div>

            <div class="input-group">
                <label for="custom_text">Custom Text (optional)</label>
                <input type="text" id="custom_text" name="custom_text" placeholder="Enter text to replace plate">
            </div>

            <button type="button" onclick="processImage()" id="processBtn">Process Image</button>
        </form>

        <div id="result">
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <span>Processing...</span>
            </div>
            <img id="resultImage" alt="Processed image">
            <div class="error" id="error"></div>
        </div>

        <script>
            const form = document.getElementById('uploadForm');
            const processBtn = document.getElementById('processBtn');
            const loading = document.getElementById('loading');
            const resultImage = document.getElementById('resultImage');
            const errorDiv = document.getElementById('error');

            async function processImage() {
                const carImage = document.getElementById('car_image').files[0];
                if (!carImage) {
                    showError('Please select a car image');
                    return;
                }

                // Start loading state
                processBtn.disabled = true;
                loading.style.display = 'flex';
                resultImage.style.display = 'none';
                errorDiv.style.display = 'none';

                const formData = new FormData();
                formData.append('car_image', carImage);

                const customImg = document.getElementById('custom_image').files[0];
                const customText = document.getElementById('custom_text').value.trim();

                if (customImg) formData.append('custom_image', customImg);
                if (customText) formData.append('custom_text', customText);

                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const blob = await response.blob();
                        resultImage.src = URL.createObjectURL(blob);
                        resultImage.style.display = 'block';
                    } else {
                        showError(await response.text());
                    }
                } catch (error) {
                    showError('Error processing image: ' + error.message);
                } finally {
                    // End loading state
                    processBtn.disabled = false;
                    loading.style.display = 'none';
                }
            }

            function showError(message) {
                errorDiv.textContent = 'Error: ' + message;
                errorDiv.style.display = 'block';
                resultImage.style.display = 'none';
            }
        </script>
    </body>
    </html>
    """)

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
                # Create a black background for the text
                car_img[y1:y2, x1:x2] = (0, 0, 0)
                font_scale = min(w, h) / 50  # Adjust font size based on plate size
                # Calculate text position to center it
                text_size = cv2.getTextSize(custom_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                text_x = x1 + (w - text_size[0]) // 2
                text_y = y1 + (h + text_size[1]) // 2
                cv2.putText(car_img, custom_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                           font_scale, (255, 255, 255), 2, cv2.LINE_AA)  # White text

            # Convert the image to bytes and return it
            _, buffer = cv2.imencode(".jpg", car_img)
            return send_file(io.BytesIO(buffer), mimetype="image/jpeg")
        else:
            return "No license plate detected", 400
    except Exception as e:
        return f"Error processing image: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)