from re import TEMPLATE


TEMPLATE = {
    "tag": "cls",
    "openvino": {
        "model_path": "./task/classification_sample/model/resnet_v1_50_inference.xml",
        "label_path": "./task/classification_sample/model/imagenet.names",
        "loop": False,
        "output": False,
        "device": "CPU",
        "thres": 0.98,
        "num_infer_requests": 0,
        "num_streams": "",
        "num_threads": None,
        "number_top": 1,
        "config": None,
        "output_resolution": None,
        "utilization_monitors": ""
    }
}