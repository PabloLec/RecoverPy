#!/bin/bash

set -o errexit -o pipefail -o nounset

### TODO ###
#- Emulate a block device and mount it
#- Add relevant python tests for this env
############

git clone https://github.com/PabloLec/recoverpy.git
cd recoverpy
python3 -m pip install . --use-feature=in-tree-build

pytest
