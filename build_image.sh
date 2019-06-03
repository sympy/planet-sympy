#!/bin/bash

set -e
set -x

docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
image_base_name=planet-sympy
image_version=${CI_COMMIT_SHA:0:7}
DNAME="$CI_REGISTRY_IMAGE:$image_version"
DNAME2="$CI_REGISTRY_IMAGE:latest"

docker build -t "$DNAME" -t "$DNAME2" .

docker push "$DNAME"
docker push "$DNAME2"
