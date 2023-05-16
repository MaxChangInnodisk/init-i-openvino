# iAPP register Sample
iAPP register Sample, this sample demonstrates how to do register customize application and use on [iVIT-I](../../README.md).

# Usage
You need to follow the step below to do register :  
Step 1. [Init ivitAppHandler ](#init-ivitapphandler).  
Step 2. [Register Application](#register-application).  
Step 3. [Use customize application](#use-customize-application) on iVIT-I.

[Another function](#another-function) for iAPP register.
## Init ivitAppHandler 
Before starting , you must creat instance for iAPP_HANDLER.  
    

        # import register from ivit-i app
        from ivit_i.common.app import iAPP_CLS, iAPP_OBJ, iAPP_SEG, iAPP_HANDLER

        # creat instance for register
        app_handler = iAPP_HANDLER()

    
## Register Application
After you have created instance for iAPP_HANDLER , you can use iAPP_HANDLER to register your application.

        # sample application
        class CustomClsApp(iAPP_CLS):
        
            def __init__(self):
                """ Do nothing """
                pass
            
            def __call__(self):
                """ Do nothing """
                return 'This is custom classification application'

        #CustomClsApp.__name__ -> Your application (instance) name during you use ivit-app.
        #CustomClsApp -> Your application (class).

        app_handler.register(CustomClsApp.__name__, CustomClsApp)

## Use customize application
More information about use application [here](../../apps/README.md).
    
        config = {...}
        label_path = "..."
        app = app_handler.get_app(CustomClsApp.__name__)( config , label_path )

## Another function
You can use these functions to manage your iAPP.

        # Get what application task that iAPP support.
        app_handler.get_sup_type() #example:iAPP_HANDLER Support ['CLS', 'OBJ', 'SEG']

        # Get all application you register.
        app_handler.get_all_apps() #example:{'CustomClsApp': <class '__main__.CustomClsApp'> }

        # Get all application after sorted by application task.
        app_handler.get_sort_apps() #example:{'CLS': ['CustomClsApp'], 'OBJ': ['CustomObjApp'], 'SEG': ['CustomSegApp']}
    
        #Get specific application task.
        app_handler.get_type_app('CLS') #example: ['CustomClsApp']