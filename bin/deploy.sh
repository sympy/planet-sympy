#! /bin/bash
#
# Deployes the latest image from docker hub on the server. This script can be
# executed from anywhere. Change XXX_DEPLOY_TOKEN_XXX to the actual deploy
# token. Otherwise no other changes are needed.

set -e
set -x

docker pull certik/planet-sympy:latest
docker stop planet
docker rm planet
docker rmi certik/planet-sympy:current
docker tag certik/planet-sympy:latest certik/planet-sympy:current
docker run -d --name planet -e DEPLOY_TOKEN=XXX_DEPLOY_TOKEN_XXX -e DEPLOY_KEY_FILE=../deploy certik/planet-sympy:latest
