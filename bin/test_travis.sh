#! /usr/bin/env bash

# Exit on error
set -e
set -x

# Do *not* echo commands (so that we don't reveal GH_TOKEN)
set +x

echo "docker run -it -e DEPLOY_TOKEN=GH_TOKEN -e TRAVIS=true test/planet-sympy"
docker run -it -e DEPLOY_TOKEN=${GH_TOKEN} -e TRAVIS=true test/planet-sympy
