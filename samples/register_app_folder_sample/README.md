# iAPP register from folder Sample
iAPP register Sample, this sample demonstrates how to do register customize application from folder and use them on [iVIT-I](../../README.md).

# Usage
You need to follow the step below to do register :  
Step 1. [Init ivitAppHandler ](#init-ivitapphandler).  
Step 2. [Register Application](#register-application) from folder.  
Step 3. [Use customize application](#use-customize-application) on iVIT-I.

[Another function](#another-function) for iAPP register.
## Init ivitAppHandler 
Before starting , you must creat instance for iAPP_HANDLER.  
    

        # import register from ivit-i app
        from ivit_i.common.app import iAPP_HANDLER

        # creat instance for register
        app_handler = iAPP_HANDLER()

    
## Register Application
After you have created instance for iAPP_HANDLER , you can use iAPP_HANDLER to register your application from folder.

        
        path_to_application_folder = "..."
        app_handler.register_from_folder(path_to_application_folder)

## Use customize application
More information about use application [here](../../apps/README.md).
    
        config = {...}
        label_path = "..."
        app = app_handler.get_app("CustomObjApp")( config , label_path )

## Another function
You can use these functions to manage your iAPP.

        # Get all application you register.
        app_handler.get_all_apps() #example: {'CustomObjApp': <class 'CustomObjApp.CustomObjApp'>, 'CustomSegApp': <class  'CustomSegApp.CustomSegApp'>}

        # Get all application after sorted by application task.
        app_handler.get_sort_apps() #example:{'OBJ': ['CustomObjApp'], 'SEG': ['CustomSegApp']}
    
        #Get specific application task.
        app_handler.get_type_app('CLS') #example: [ ]