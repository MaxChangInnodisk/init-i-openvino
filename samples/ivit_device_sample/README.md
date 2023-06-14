# IVIT-I iDEVICE 
iVIT-I iDEVICE Sample, this sample demonstrates how to do use iDEVICE to monitor device on [iVIT](../../README.md).

# Usage
* Create instance for iDevice.
    ```bash
    #import iDevice from ivit
    from ivit_i.utils import iDevice 

    idev = iDevice()

    ```
* Another useful function.  
    1. Use `idev.get_device_info()` can get all device information, and the format of return like below.  

    

        ```bash

        {   #CPU information.
            'CPU':{
                    'id': 0,                            # the idex wget from device. 
                    'uid': 'CPU',                      # the name get from device. 
                    'load': 0,                          # loading capacity get from device. 
                    'memoryUtil': 0,                    # amount of memory usage get from device. 
                    'temperature': 30.857142857142858   # temperature get from device
                  }, 
            #GNA information.   
            'GNA':{
                    'id': 1,                            # the idex wget from device. 
                    'uid': 'GNA',                      # the name get from device. 
                    'load': 0,                          # loading capacity get from device. 
                    'memoryUtil': 0,                    # amount of memory usage get from device. 
                    'temperature': 30.857142857142858   # temperature get from device
                  }, 
            #GPU information.      
            'GPU':{
                    'id': 2,                            # the idex wget from device.s
                    'uid': 'GPU',                      # the name get from device. 
                    'load': 0,                          # loading capacity get from device.
                    'memoryUtil': 0,                    # amount of memory usage get from device.
                    'temperature': 30.857142857142858   # temperature get from device
                  }
        }


        ```
    2. Use `idev.get_device_info('CPU')` can get target device information,and the format of return like below.

        ```bash

        
        {
            "CPU":{
                'id': 0,                            # the idex wget from device.
                'uid': 'CPU',                      # the name get from device. 
                'load': 0,                          # loading capacity get from device.
                'memoryUtil': 0,                    # amount of memory usage get from device.
                'temperature': 30.857142857142858   # temperature get from device
            }
        }
    