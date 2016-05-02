#! /bin/bash

set -e
set -x

GH_TOKEN=$1

echo -e  'y\n' | ssh-keygen -P "" -f travisdeploykey
openssl aes-256-cbc -k ${GH_TOKEN} -in travisdeploykey -out ../travisdeploykey.enc

docker build -t certik/travis:v1 .

docker run -i -v ${PWD}:/home/swuser/data certik/travis:v1 sh <<EOF
set -e
set -x
travis encrypt -r sympy/planet-sympy DEPLOY_TOKEN=${GH_TOKEN}
EOF
