import cv2
import numpy as np
from safevision_face.feature_extraction.edgeface_extractor import EdgeFaceFeatureExtractor

_extractor = None

def _get_extractor():
    global _extractor
    if _extractor is None:
        _extractor = EdgeFaceFeatureExtractor()
    return _extractor


def face_extraction(image_bgr: np.ndarray):
    extractor = _get_extractor()
    embedding = extractor.predict(image_bgr)
    if not isinstance(embedding, np.ndarray):
        embedding = embedding.cpu().numpy()
    return embedding
