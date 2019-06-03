#!/bin/bash

set -e
set -x

docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" $CI_REGISTRY
image_base_name=planet-sympy
image_version=${CI_COMMIT_SHA:0:7}
if [[ $CI_COMMIT_REF_NAME == "master" ]]; then
    DNAME="$CI_REGISTRY_IMAGE:$image_version"
    DNAME2="$CI_REGISTRY_IMAGE:latest"
else
    DNAME="$CI_REGISTRY_IMAGE/ci-test:$image_version"
    DNAME2="$CI_REGISTRY_IMAGE/ci-test:latest"
fi

docker build -t "$DNAME" -t "$DNAME2" .

docker push "$DNAME"
docker push "$DNAME2"
