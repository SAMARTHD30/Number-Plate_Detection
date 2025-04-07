# License Plate Detection API

A FastAPI-based REST API for detecting and processing license plates in images using YOLO.

## Setup
0. Clone the repository:
```bash
git clone https://github.com/SAMARTHD30/Number-Plate_Detection-.git
cd license-plate-detection-api
```

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

1. `POST /api/v1/detect`
   - Detects license plates in an image
   - Request: Form data with `image` file
   - Response: JSON with detection boxes

2. `POST /api/v1/process`
   - Processes an image by replacing detected license plate with custom content
   - Request: Form data with:
     - `car_image`: Main image file
     - `custom_image`: (Optional) Image to replace license plate
     - `custom_text`: (Optional) Text to replace license plate
   - Response: Processed image file

## Example Usage

Using curl:

```bash
# Detect license plate
curl -X POST "http://localhost:8000/api/v1/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@path/to/your/image.jpg"

# Process image with custom text
curl -X POST "http://localhost:8000/api/v1/process" \
     -H "accept: image/jpeg" \
     -H "Content-Type: multipart/form-data" \
     -F "car_image=@path/to/car.jpg" \
     -F "custom_text=ABC123"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
