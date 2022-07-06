# Configure Environment ( `init-i.json` )

We use [init-i.json](../init-i.json) to configure environment.


| Key       | Sample            | Describe
| ---       | ---               | --- 
| PROJECT   | init-i            | project name
| VERSION   | v0.1              | docker image version
| PLATFORM  | intel             | the platform name, etc. nvidia, intel, xilinx
| FRAMEWORK | openvino          | tensorrt (nvidia), openvino (intel), vitis-ai (xilinx)
| AF        | openvino          | same with FRAMEWORK
| HOST      |                 | ip address, it will capture automatically if not setting.
| PORT      | 819               | port number, 819 for intel
| LOGGER    | init-i-web.log    | logger name
| TASK_ROOT | task              | AI task directory
| DATA      | data              | path to meta data
| TEMP_PATH | temp              | path to temporary folder
| DEBUG     | false             | setup debug mode for web api
| WORKER    | 1                 | setup worker for web api
| THREADING | 30                | setup threads limit for web api
