#! /usr/bin/env bash

# Exit on error
set -e
set -x

# Do *not* echo commands (so that we don't reveal DEPLOY_TOKEN)
set +x

echo 'docker run -e DEPLOY_TOKEN=${DEPLOY_TOKEN} -e TRAVIS=true test/planet-sympy'
docker run -e DEPLOY_TOKEN=${DEPLOY_TOKEN} -e TRAVIS=true test/planet-sympy
