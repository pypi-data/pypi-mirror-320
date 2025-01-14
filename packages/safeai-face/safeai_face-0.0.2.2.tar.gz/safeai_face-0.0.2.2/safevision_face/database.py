from pymilvus import MilvusClient
import numpy as np
import time
import os

from .config import DEFAULT_DB_PATH, DEFAULT_COLLECTION_NAME, DEFAULT_DIMENSION, DEFAULT_METRIC, DEFAULT_INDEX, DEFAULT_NLIST, DEFAULT_NPROBE

def db_set(
    db_path: str = DEFAULT_DB_PATH,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    dimension: int = DEFAULT_DIMENSION,
    metric_type: str = DEFAULT_METRIC,
    indexing: str = DEFAULT_INDEX,
    nlist: int = DEFAULT_NLIST,
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
    else:
        index_info = client.describe_index(collection_name=collection_name, index_name="ivf_flat_index")
        if index_info:
            client.drop_index(
                collection_name=collection_name,
                index_name="ivf_flat_index"
            )
        
    index_params = MilvusClient.prepare_index_params()
    
    index_params.add_index(
        field_name="vector",
        index_type=DEFAULT_INDEX,
        index_name="ivf_flat_index",
        metric_type=metric_type,
        params={"nlist":DEFAULT_NLIST}
    )
    
    client.create_index(
        collection_name=collection_name,
        index_params=index_params
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
    metric_type: str = DEFAULT_METRIC,
    top_k: int = 5,
    threshold: float = 0.4,
    nprobe: int = DEFAULT_NPROBE,
    extractor_func=None,
):

    if extractor_func is None:
        raise ValueError("extractor_func is required. (e.g. face_extraction)")
    query_vector = extractor_func(query_image)
    if not isinstance(query_vector, list):
        query_vector = query_vector.tolist()
        
    search_params = {
        "metric_type": DEFAULT_METRIC,
        "params": {"nprobe":DEFAULT_NPROBE}
    }

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
        search_param=search_params,
    )

    hits = []
    for hit in results[0][:top_k]:
        score = hit["distance"]
        if score >= threshold:
            hits.append({
                "score": score,
                "entity": hit["entity"]
            })

    return hits
