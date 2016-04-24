#! /usr/bin/env bash

# Exit on error
set -e
# Do *not* echo commands (so that we don't reveal GH_TOKEN)
set +x

echo "docker run -e DEPLOY_TOKEN=GH_TOKEN -e TRAVIS=yes test/planet-sympy"
docker run -e DEPLOY_TOKEN=${GH_TOKEN} -e TRAVIS=yes test/planet-sympy
