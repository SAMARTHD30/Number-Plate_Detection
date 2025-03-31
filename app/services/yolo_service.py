from ultralytics import YOLO
import cv2
import numpy as np
import torch
from contextlib import contextmanager
from typing import List, Tuple

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

class YOLOService:
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: str) -> YOLO:
        try:
            with allow_unsafe_load():
                model = YOLO(model_path, task='detect')
            return model
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")

    def detect_plates(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        results = self.model(image)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        return [tuple(map(int, box)) for box in boxes]

    def process_image(self, image: np.ndarray, custom_text: str = None, custom_image: np.ndarray = None) -> np.ndarray:
        boxes = self.detect_plates(image)
        if not boxes:
            raise ValueError("No license plate detected in the image")

        x1, y1, x2, y2 = boxes[0]
        w, h = x2 - x1, y2 - y1

        if custom_image is not None:
            custom_img = cv2.resize(custom_image, (w, h))
            image[y1:y2, x1:x2] = custom_img
        elif custom_text:
            image[y1:y2, x1:x2] = (255, 255, 255)
            font_scale = min(w, h) / 50
            text_size = cv2.getTextSize(custom_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
            text_x = x1 + (w - text_size[0]) // 2
            text_y = y1 + (h + text_size[1]) // 2
            cv2.putText(image, custom_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, (0, 0, 0), 2, cv2.LINE_AA)

        return image