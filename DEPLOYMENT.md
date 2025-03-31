# License Plate Detection API - Deployment Guide

## Prerequisites
- Python 3.8 or higher
- Git
- Your own YOLO model file (`best.pt`)

## Installation Steps

1. Clone the repository:
```bash
git clone <your-repository-url>
cd license-plate-app
```

2. Create and activate virtual environment:
```bash
# On Windows (Git Bash):
python -m venv venv
source venv/Scripts/activate

# On Linux/Mac:
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Place your YOLO model:
- Copy your `best.pt` file to the root directory of the project

5. Run the API:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage Guide

### Endpoints

1. **Detect License Plate**
```
POST /api/v1/detect
Content-Type: multipart/form-data

Parameters:
- image: Image file (required)
```

Example Response:
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

2. **Process Image**
```
POST /api/v1/process
Content-Type: multipart/form-data

Parameters:
- car_image: Main image file (required)
- custom_image: Custom image to replace plate (optional)
- custom_text: Text to replace plate (optional)
```

Example Response:
- Returns processed image as JPEG

### Example Usage with curl

1. Detect license plate:
```bash
curl -X POST "http://your-server:8000/api/v1/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@path/to/your/image.jpg"
```

2. Process image with custom text:
```bash
curl -X POST "http://your-server:8000/api/v1/process" \
     -H "accept: image/jpeg" \
     -H "Content-Type: multipart/form-data" \
     -F "car_image=@path/to/car.jpg" \
     -F "custom_text=ABC123"
```

### Example Usage with Python

```python
import requests

# Detect license plate
def detect_plate(image_path):
    url = "http://your-server:8000/api/v1/detect"
    files = {"image": open(image_path, "rb")}
    response = requests.post(url, files=files)
    return response.json()

# Process image
def process_image(car_image_path, custom_text=None, custom_image_path=None):
    url = "http://your-server:8000/api/v1/process"
    files = {"car_image": open(car_image_path, "rb")}
    if custom_image_path:
        files["custom_image"] = open(custom_image_path, "rb")
    data = {"custom_text": custom_text} if custom_text else {}

    response = requests.post(url, files=files, data=data)
    return response.content

# Example usage
detections = detect_plate("car.jpg")
processed_image = process_image("car.jpg", custom_text="ABC123")
```

## Important Notes

1. **Security**:
   - The API is running on port 8000 by default
   - Make sure to configure your firewall to allow access to this port
   - Consider adding authentication for production use

2. **Performance**:
   - The API uses YOLO for detection, which requires significant computational resources
   - Ensure your server has adequate RAM and GPU (if using GPU acceleration)

3. **Error Handling**:
   - The API returns appropriate HTTP status codes and error messages
   - Common errors:
     - 400: Invalid input (e.g., no image provided)
     - 500: Server error (e.g., model loading issues)

4. **Rate Limiting**:
   - Consider implementing rate limiting for production use
   - Monitor server resources to prevent overload

## Troubleshooting

1. **Model Loading Issues**:
   - Ensure `best.pt` is in the correct location
   - Check if you have sufficient RAM/GPU memory

2. **Connection Issues**:
   - Verify the server is running (`uvicorn app.main:app --host 0.0.0.0 --port 8000`)
   - Check firewall settings
   - Ensure correct IP/port in API calls

3. **Image Processing Errors**:
   - Verify image format (JPEG, PNG supported)
   - Check image size (large images may cause memory issues)
   - Ensure image is not corrupted