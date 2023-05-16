# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from ivit_i.common.app import iAPP_OBJ

class CustomObjApp(iAPP_OBJ):
    
    def __init__(self):
        """ Do nothing """
        pass
     
    def __call__(self):
        """ Do nothing """
        return "Hi, This is custom object detection application"
