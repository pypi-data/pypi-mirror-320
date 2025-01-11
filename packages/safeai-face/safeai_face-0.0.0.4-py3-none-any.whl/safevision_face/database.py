from pymilvus import MilvusClient
import numpy as np
import time
import os

from .config import DEVICE, DEFAULT_YOLO_MODEL_PATH, DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_IOU_THRESHOLD, DEFAULT_PADDING

def db_set(
    db_path: str = DEFAULT_DB_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    dimension: int = DEFAULT_DIMENSION,
    metric_type: str = DEFAULT_METRIC,
    auto_id: bool = True,
    enable_dynamic_field: bool = True
):

    client = MilvusClient(uri=db_path)
    if not client.has_collection(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vector_field_name="vector",
            dimension=dimension,
            auto_id=auto_id,
            enable_dynamic_field=enable_dynamic_field,
            metric_type=metric_type,
        )
    return client


def db_insert(
    client: MilvusClient,
    collection_name: str,
    vector: np.ndarray,
    orig_path: str,
    crop_path: str,
    timestamp: str,
    tracking_id: int,
    cam_id: str
):

    if not isinstance(vector, list):
        vector = vector.tolist()

    data_dict = {
        "vector": vector,
        "orig_path": orig_path,
        "crop_path": crop_path,
        "timestamp": timestamp,
        "tracking_id": tracking_id,
        "cam_id": cam_id,
    }
    client.insert(collection_name=collection_name, data=data_dict)
    return True

def db_search(
    client: MilvusClient,
    collection_name: str,
    query_image: np.ndarray,
    top_k: int = 5,
    threshold: float = 0.4,
    extractor_func=None,
):

    if extractor_func is None:
        raise ValueError("extractor_func is required. (e.g. face_extraction)")
    query_vector = extractor_func(query_image)
    if not isinstance(query_vector, list):
        query_vector = query_vector.tolist()

    results = client.search(
        collection_name=collection_name,
        data=[query_vector],
        output_fields=[
            "timestamp", 
            "orig_path", 
            "crop_path", 
            "tracking_id", 
            "cam_id"
        ],
        param={"metric_type": "COSINE"},
        limit=top_k
    )

    hits = []
    for hit in results[0]:
        score = hit.distance
        if score >= threshold:
            hits.append({
                "score": score,
                "entity": hit.entity
            })

    return hits
