#!/bin/bash

set -e
set -x

# LC_ALL is set in the Dockerfile now

./build.sh

if [[ "${TESTING}" == "true" ]]; then
    # Use testing setup for CI
    REPO_SUFFIX="-test"
else
    # Production setup
    REPO_SUFFIX=""
fi

git clone https://github.com/planet-sympy/planet.sympy.org${REPO_SUFFIX}
cd planet.sympy.org${REPO_SUFFIX}

git config user.name "Planet SymPy Bot"
git config user.email "noreply@sympy.org"
COMMIT_MESSAGE="Publishing site on $(date "+%Y-%m-%d %H:%M:%S")"

git checkout -t origin/gh-pages || git checkout gh-pages
rm -rf ./*
cp -r ../build/website/* .
if [[ "${TESTING}" != "true" ]]; then
    echo "planet.sympy.org" > CNAME
fi
touch .nojekyll
git add -A .
git commit -m "${COMMIT_MESSAGE}"

echo "Deploying:"

if [[ "${SSH_PRIVATE_KEY}" == "" ]]; then
    echo "Not deploying because SSH_PRIVATE_KEY is empty."
    exit 0
fi

git push origin gh-pages