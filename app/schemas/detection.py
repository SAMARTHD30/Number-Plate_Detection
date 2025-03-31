from pydantic import BaseModel
from typing import List, Optional

class DetectionBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class DetectionResponse(BaseModel):
    detections: List[DetectionBox]

class ProcessRequest(BaseModel):
    custom_text: Optional[str] = None