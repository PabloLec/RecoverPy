#!/bin/bash

set -o errexit -o pipefail -o nounset

git clone https://github.com/PabloLec/recoverpy.git
cd recoverpy
python3 -m pip install -r requirements.txt
