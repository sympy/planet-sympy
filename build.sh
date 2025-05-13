#!/bin/bash

set -e
set -x

mkdir -p build
cp -R planet/* build/

# Using our new planet.py instead of rawdog
cd build
echo "Running planet.py"
../planet.py -d planetsympy/ --update --write