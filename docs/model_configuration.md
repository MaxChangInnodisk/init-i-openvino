# Configurate Model

If you want to change your model of openvino and parameters, you should be changed the content of task/example_sample/example.json 

```json
{  
    "tag":"class",
    "openvino":{
        "model_path":"resnet_v1_50_inference.xml",
        "label_path":"iamgenet.names",
        "device":"CPU",
    }
}
```
|   Key         |   Describe    |
|   ---         |   ---         |
|   model_path  |   path to model
|   label_path  |   path to label   
|   device      |   accelerator, etc. [ CPU, GPU, MYRIAD ]