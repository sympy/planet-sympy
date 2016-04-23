#! /bin/bash

set -e
set -x

GH_TOKEN=$1

docker build -t certik/travis:v1 .

echo -e  'y\n' | ssh-keygen -P "" -f travisdeploykey
chmod 644 travisdeploykey

docker run -i -v ${PWD}:/home/swuser/data certik/travis:v1 sh <<EOF
set -e
set -x
travis login --github-token=${GH_TOKEN}
travis encrypt-file -r sympy/planet-sympy data/travisdeploykey
EOF

docker cp $(docker ps -l -q):/home/swuser/travisdeploykey.enc .

chmod 600 travisdeploykey
