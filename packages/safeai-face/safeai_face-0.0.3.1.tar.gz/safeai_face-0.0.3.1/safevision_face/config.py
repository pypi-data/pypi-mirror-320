
import torch
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DEFAULT_YOLO_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
YOLO_CHECKPOINT = os.path.join(DEFAULT_YOLO_MODEL_PATH, "yolov11m-face.pt")

DEFAULT_DB_PATH = "./"
DEFAULT_COLLECTION_NAME = "face_collection"
DEFAULT_DIMENSION = 512
DEFAULT_METRIC = "COSINE"
DEFAULT_CONFIDENCE_THRESHOLD = 0.45
DEFAULT_IOU_THRESHOLD = 0.4

DEFAULT_INDEX = "IVF_FLAT"
DEFAULT_NLIST = 128
DEFAULT_NPROBE = 16

DEFAULT_PADDING = 5
