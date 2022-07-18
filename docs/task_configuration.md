# Configure AI Task

```json
{
    "name": "classification_sample",
    "framework": "openvino",
    "prim": {
        "model_json": "./task/classification_sample/classification.json"
    },
    "source_type": "Image",
    "source": "data/cat.jpg",
    "application": {
        "name": "default",
        "depend_on": [ "car", "cat", "person" ],
    },
}
```
|   Key         |   Describe    |
|   ---         |   ---         |
|   name        |   the name of AI tasks
|   framework   |   AI framework for double check  
|   model_json  |   path to primary model configuration
|   source      |   the source of meta data
|   source_type |   the type of source
|   application |   setup application
