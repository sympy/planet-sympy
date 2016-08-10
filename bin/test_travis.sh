#! /usr/bin/env bash

# Exit on error
set -e
set -x

# Do *not* echo commands (so that we don't reveal DEPLOY_TOKEN)
set +x

echo 'docker run -e SSH_PRIVATE_KEY="${SSH_PRIVATE_KEY}" -e TESTING=true test/planet-sympy'
docker run -e SSH_PRIVATE_KEY="${SSH_PRIVATE_KEY}" -e TESTING=true test/planet-sympy
