# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

#!/bin/bash
pdoc3 --html --force \
--skip-error \
-c show_source_code=False \
ivit_i

rm -rf ./docs
mv -f ./html/ivit_i ./docs
rm -rf ./html