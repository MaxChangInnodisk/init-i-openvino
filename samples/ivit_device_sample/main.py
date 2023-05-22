# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
iDevice Usage
"""

import sys, os
from ivit_i.utils import iDevice 

print_title = lambda title: print(f'\n# {title}')
idev = iDevice()

print_title('Get Available Devices')
print(idev.get_available_device())

print_title('Get All Device Information')
print(idev.get_device_info())
