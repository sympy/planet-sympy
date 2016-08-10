#! /bin/bash

set -e
set -x

cp -r planet/* testrun/
cd testrun
./rawdog -d planetsympy/ --update
./rawdog -d planetsympy/ --write
cd ..

if [[ "${TESTING}" == "true" ]]; then
    # Use testing setup for Travis
    REPO_SUFFIX="-test"
else
    # Production setup
    REPO_SUFFIX=""
fi

git clone https://github.com/planet-sympy/planet.sympy.org${REPO_SUFFIX}
cd planet.sympy.org${REPO_SUFFIX}

git config user.name "Docker"
git config user.email "noreply@docker.org"
COMMIT_MESSAGE="Publishing site on `date "+%Y-%m-%d %H:%M:%S"`"

git checkout -t origin/gh-pages
rm -rf *
cp -r ../testrun/website/* .
if [[ "${TESTING}" != "true" ]]; then
    echo "planet.sympy.org" > CNAME
fi
git add -A .
git commit -m "${COMMIT_MESSAGE}"


echo "Deploying:"

mkdir ~/.ssh
chmod 700 ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts

eval `ssh-agent -s`

set +x
if [[ "${SSH_PRIVATE_KEY}" == "" ]]; then
    echo "Not deploying because SSH_PRIVATE_KEY is empty."
    exit 0
fi
# Generate the private/public key pair using:
#
#     ssh-keygen -f deploy_key -N ""
#
# then set the $SSH_PRIVATE_KEY environment variable in the CI (Travis-CI,
# GitLab-CI, ...) to the base64 encoded private key:
#
#     cat deploy_key | base64 -w0
#
# and add the public key `deploy_key.pub` into the target git repository (with
# write permissions).

ssh-add <(echo "$SSH_PRIVATE_KEY" | base64 --decode)
set -x

git push git@github.com:planet-sympy/planet.sympy.org${REPO_SUFFIX} gh-pages
