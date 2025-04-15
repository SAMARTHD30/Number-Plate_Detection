# License Plate Detection API

A FastAPI-based REST API for detecting and processing license plates in images using YOLO.

## Setup
0. Clone the repository:
```bash
git clone https://github.com/SAMARTHD30/Number-Plate_Detection-.git
cd license-plate-detection-api
```

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure you have your YOLO model file (`best.pt`) in the root directory

4. Run the API:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

1. `GET /api/v1/ping`
   - Check API status
   - Response: JSON with status message

2. `POST /api/v1/detect`
   - Detects license plates in an image
   - Request: Form data with `image` file
   - Response: JSON with detection boxes

3. `POST /api/v1/process`
   - Processes an image by replacing detected license plate with custom content
   - Request: Form data with:
     - `car_image`: Main image file
     - `custom_image`: (Optional) Image to replace license plate
     - `custom_text`: (Optional) Text to replace license plate
   - Response: Processed image file

4. `GET /api/v1/image/{image_id}`
   - Retrieve a processed image
   - Response: Image file

## Example Usage

Using curl:

```bash
# Check API status
curl -X GET http://localhost:8000/ping

# Detect license plate
curl -X POST -F "image=@path/to/image.jpg" http://localhost:8000/detect

# Process image with custom text
curl -X POST \
  -F "car_image=@path/to/car.jpg" \
  -F "custom_text=Your Text" \
  -F "custom_image=@path/to/custom.jpg" \
  http://localhost:8000/process

# Get processed image
curl -X GET http://localhost:8000/image/{image_id}
```

Using Python:
```python
import requests

# Check API status
response = requests.get("http://localhost:8000/api/v1/ping")
print(response.json())

# Detect license plate
def detect_plate(image_path):
    with open(image_path, "rb") as f:
        files = {"image": f}
        response = requests.post(
            "http://localhost:8000/api/v1/detect",
            files=files
        )
    return response.json()

# Process image
def process_image(car_image_path, custom_text=None):
    with open(car_image_path, "rb") as f:
        files = {"car_image": f}
        data = {"custom_text": custom_text} if custom_text else {}
        response = requests.post(
            "http://localhost:8000/api/v1/process",
            files=files,
            data=data
        )
    return response.content

# Get processed image
def get_processed_image(image_id):
    response = requests.get(
        f"http://localhost:8000/api/v1/image/{image_id}",
        headers={"accept": "image/jpeg"}
    )
    with open(f"processed_{image_id}.jpg", "wb") as f:
        f.write(response.content)
    return f"processed_{image_id}.jpg"

# Example usage
status = requests.get("http://localhost:8000/api/v1/ping").json()
print(f"API Status: {status}")

detections = detect_plate("car.jpg")
print(f"Detections: {detections}")

processed_image = process_image("car.jpg", custom_text="ABC123")
with open("processed.jpg", "wb") as f:
    f.write(processed_image)

# Get the processed image
image_path = get_processed_image("123")
print(f"Saved processed image to: {image_path}")
```

## Response Examples

1. **Ping Response**:
```json
{
    "status": "ok",
    "message": "API is running",
    "version": "1.0.0"
}
```

2. **Detection Response**:
```json
{
    "detections": [
        {
            "x1": 100,
            "y1": 200,
            "x2": 300,
            "y2": 400
        }
    ]
}
```

3. **Process Response**:
- Returns processed image as JPEG file

4. **Get Image Response**:
- Returns requested image as JPEG file

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
