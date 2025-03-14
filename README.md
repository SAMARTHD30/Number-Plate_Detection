# License Plate Editor

A Flask web application that uses YOLOv8 to detect and replace license plates in images. The application allows users to upload a car image and either replace the detected license plate with custom text or another image.

## Features

- License plate detection using YOLOv8
- Upload car images for processing
- Replace detected license plates with:
  - Custom text
  - Custom images
- Modern, responsive UI
- Real-time processing feedback

## Prerequisites

- Python 3.8 or higher
- PyTorch
- OpenCV
- Flask
- Ultralytics YOLOv8

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/license-plate-app.git
cd license-plate-app
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Download the YOLOv8 model:

- Place your trained `best.pt` model file in the root directory
- Or use a pre-trained model from Ultralytics

## Usage

1. Start the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

3. Upload a car image and optionally:

   - Upload a custom image to replace the license plate
   - Enter custom text to replace the license plate

4. Click "Process Image" to detect and replace the license plate

## Project Structure

```
license-plate-app/
├── app.py              # Main Flask application
├── best.pt            # YOLOv8 model weights
├── requirements.txt   # Python dependencies
└── README.md         # Project documentation
```

## Technical Details

- Built with Flask for the backend
- Uses YOLOv8 for license plate detection
- OpenCV for image processing
- Modern UI with responsive design
- Error handling and loading states

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
