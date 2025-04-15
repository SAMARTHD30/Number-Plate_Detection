from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import numpy as np
import io
import uuid
from app.services.yolo_service import YOLOService
from app.schemas.detection import DetectionResponse, ProcessRequest
from typing import Dict

router = APIRouter()
yolo_service = YOLOService("best.pt")

@router.get("/ping", response_model=Dict[str, str])
async def ping():
    """Check API status"""
    return {
        "status": "ok",
        "message": "API is running",
        "version": "1.0.0"
    }

@router.post("/detect", response_model=DetectionResponse)
async def detect_plate(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        image_array = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        boxes = yolo_service.detect_plates(image)
        if not boxes:
            return DetectionResponse(detections=[])

        detections = [{"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                     for x1, y1, x2, y2 in boxes]

        return DetectionResponse(detections=detections)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process", response_model=Dict[str, str])
async def process_image(
    car_image: UploadFile = File(...),
    custom_image: UploadFile = File(None),
    custom_text: str = Form(None)
):
    try:
        # Read car image
        car_contents = await car_image.read()
        car_array = np.frombuffer(car_contents, np.uint8)
        car_img = cv2.imdecode(car_array, cv2.IMREAD_COLOR)

        if car_img is None:
            raise HTTPException(status_code=400, detail="Invalid car image file")

        # Read custom image if provided
        custom_img = None
        if custom_image:
            custom_contents = await custom_image.read()
            custom_array = np.frombuffer(custom_contents, np.uint8)
            custom_img = cv2.imdecode(custom_array, cv2.IMREAD_COLOR)
            if custom_img is None:
                raise HTTPException(status_code=400, detail="Invalid custom image file")

        # Process the image
        processed_img = yolo_service.process_image(
            car_img,
            custom_text=custom_text,
            custom_image=custom_img
        )

        # Generate a unique ID for the image
        image_id = str(uuid.uuid4())

        # Save the processed image (in a real app, you'd save to storage)
        # For now, we'll just return the ID
        return {"image_id": image_id}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/image/{image_id}")
async def get_image(image_id: str):
    """Retrieve a processed image by ID"""
    try:
        # In a real application, you would retrieve the image from storage
        # For now, we'll return a placeholder image
        placeholder = np.zeros((100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", placeholder)
        return StreamingResponse(io.BytesIO(buffer), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))