# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
iDevice Usage
"""

import sys, os
sys.path.append('/workspace')
from ivit_i.utils import iDevice 

print_title = lambda title: print(f'\n# {title}')

idev = iDevice()

print_title('Get All Device Information')
print(idev.get_all_device())

print_title('Get Target Device Information')
print(idev.get_device_info('CPU'))

print_title('Get Device Index')
print(idev.get_device_id('CPU'))