#! /bin/bash

set -e
set -x

mkdir -p build
cp -R planet/* build/
(cd build
 ./rawdog -d planetsympy/ --update
 ./rawdog -d planetsympy/ --write)
