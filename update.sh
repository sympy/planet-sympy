#! /bin/bash

set -e
set -x

rm -rf testrun/*
cp -r planet/* testrun/
cd testrun
./rawdog -d planetsympy/ --update
./rawdog -d planetsympy/ --write
cd ..

if [[ "${TRAVIS}" == "true" ]]; then
    # Use testing setup for Travis
    DEPLOY_KEY_FILE=../travisdeploykey.enc
    REPO_SUFFIX="-test"
else
    # Production setup
    DEPLOY_KEY_FILE=../deploykey.enc
    REPO_SUFFIX=""
fi

rm -rf planet.sympy.org${REPO_SUFFIX}
git clone https://github.com/planet-sympy/planet.sympy.org${REPO_SUFFIX}
cd planet.sympy.org${REPO_SUFFIX}

git config user.name "Docker"
git config user.email "noreply@docker.org"
COMMIT_MESSAGE="Publishing site on `date "+%Y-%m-%d %H:%M:%S"`"

git checkout -t origin/gh-pages
rm -rf *
cp -r ../testrun/website/* .
cp ../git_revision .
if [[ "${TRAVIS}" != "true" ]]; then
    echo "planet.sympy.org" > CNAME
fi
git add -A .
git commit -m "${COMMIT_MESSAGE}"


echo "Deploying:"

if [ ! -n "$(grep "^github.com " ~/.ssh/known_hosts)" ]; then
    mkdir ~/.ssh
    chmod 700 ~/.ssh
    ssh-keyscan github.com >> ~/.ssh/known_hosts
fi

set +x
if [[ "${DEPLOY_TOKEN}" == "" ]]; then
    echo "Not deploying because DEPLOY_TOKEN is empty."
    exit 0
fi
openssl aes-256-cbc -k ${DEPLOY_TOKEN} -in ${DEPLOY_KEY_FILE} -out deploykey -d
set -x

chmod 600 deploykey
eval `ssh-agent -s`
ssh-add deploykey

git push git@github.com:planet-sympy/planet.sympy.org${REPO_SUFFIX} gh-pages
