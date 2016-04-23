set -e
set -x

rm -rf testrun/*
cp -r planet/* testrun/
cd testrun
./rawdog -d planetsympy/ --update
./rawdog -d planetsympy/ --write
cd ..

rm -rf planet.sympy.org
git clone https://github.com/planet-sympy/planet.sympy.org
cd planet.sympy.org

git config user.name "Docker"
git config user.email "noreply@docker.org"
COMMIT_MESSAGE="Publishing site on `date "+%Y-%m-%d %H:%M:%S"`"

git checkout -t origin/gh-pages
rm -rf *
cp -r ../testrun/website/* .
echo "planet.sympy.org" > CNAME
git add -A .
git commit -m "${COMMIT_MESSAGE}"


echo "Deploying:"

set +x
if [ "${DEPLOY_TOKEN}" = "" ]; then
    echo "Not deploying because DEPLOY_TOKEN is empty."
    exit 0
fi
openssl aes-256-cbc -k ${DEPLOY_TOKEN} -in ../deploykey.enc -out deploykey -d
set -x

chmod 600 deploykey
eval `ssh-agent -s`
ssh-add deploykey

if [ ! -n "$(grep "^github.com " ~/.ssh/known_hosts)" ]; then
    mkdir ~/.ssh
    chmod 700 ~/.ssh
    ssh-keyscan github.com >> ~/.ssh/known_hosts
fi

git push git@github.com:planet-sympy/planet.sympy.org gh-pages
