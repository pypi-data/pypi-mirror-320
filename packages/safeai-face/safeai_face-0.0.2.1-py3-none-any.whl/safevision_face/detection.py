# my_face_library/detection.py

import cv2
from ultralytics import YOLO
import numpy as np

from .config import DEVICE, YOLO_CHECKPOINT, DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_IOU_THRESHOLD, DEFAULT_PADDING
from .utils import padding_image

_yolo_model = None

def _get_yolo_model(model_path: str = YOLO_CHECKPOINT):
    global _yolo_model
    if _yolo_model is None:
        _yolo_model = YOLO(model_path).to(DEVICE)
    return _yolo_model


def face_detection(
    image_bgr: np.ndarray,
    conf: float = DEFAULT_CONFIDENCE_THRESHOLD,
    iou: float = DEFAULT_IOU_THRESHOLD,
    do_track: bool = False,
    tracker_config: str = "bytetrack.yaml",
):

    model = _get_yolo_model()
    
    if do_track:
        results = model.track(
            image_bgr,
            conf=conf,
            iou=iou,
            persist=True,
            tracker=tracker_config,
            verbose=False
        )
    else:
        results = model.predict(
            image_bgr,
            conf=conf,
            iou=iou,
            verbose=False
        )
    
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = padding_image(image_bgr, x1, y1, x2, y2, padding=DEFAULT_PADDING)
            
            score = float(box.conf[0]) if box.conf is not None else None
            track_id = int(box.id[0].item()) if box.id is not None else None
            detections.append({
                "box": (int(x1), int(y1), int(x2), int(y2)),
                "track_id": track_id,
                "score": score
            })
    
    return detections
