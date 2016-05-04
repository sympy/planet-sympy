#! /bin/bash

set -e
set -x

GH_TOKEN=$1
DEPLOY_TOKEN=$2

echo -e  'y\n' | ssh-keygen -P "" -f travisdeploykey
openssl aes-256-cbc -k ${DEPLOY_TOKEN} -in travisdeploykey -out ../travisdeploykey.enc

docker build -t sympy/travis:v1 .

docker run -i sympy/travis:v1 sh <<EOF
set -e
set -x
travis login --github-token=${GH_TOKEN}
travis encrypt -r sympy/planet-sympy -i DEPLOY_TOKEN=${DEPLOY_TOKEN}
EOF
