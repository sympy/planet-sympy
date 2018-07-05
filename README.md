# Sources for planet.sympy.org

## Adding a new blog

Add a new blog a the end of `planet/planetsympy/config`. Send a PR against this
repository. Travis tests must pass: Travis will build a docker image and pull
all the blogs. This will ensure that the syntax in the `config` file is
correct.

# Development

To build the site, run

    ./build.sh

This requires Python 2 and some libraries.

# Deployment


## Build docker image

    docker build -t username/planet-sympy:v1 .

## Run docker image

    docker run -d -e SSH_PRIVATE_KEY=XXX username/planet-sympy:v1

Where you change `XXX` for a base64 encoded private ssh key. This command will
update the planet and push the new files into the
https://github.com/planet-sympy/planet.sympy.org repository. If you add the `-e
TESTING=true` option, it will push into the
https://github.com/planet-sympy/planet.sympy.org-test repository (this is
useful for testing, and that is what the Travis-CI does to ensure that things
work, without uploading possibly broken results into
`planet-sympy/planet.sympy.org`).

The docker image from the latest master is automatically built at docker hub:
https://hub.docker.com/r/certik/planet-sympy/, so to download it and run it,
do:

    docker run -e SSH_PRIVATE_KEY="$SSH_PRIVATE_KEY" certik/planet-sympy:latest

And set the `SSH_PRIVATE_KEY` environment variable (typically in the Travis-CI
or GitLab-CI web interface). Generate the private/publish ssh key using:

     ssh-keygen -f deploy_key -N ""

then set the `SSH_PRIVATE_KEY` environment variable in the CI (Travis-CI,
GitLab-CI, ...) to the base64 encoded private key:

     cat deploy_key | base64 -w0

and add the public key `deploy_key.pub` into the target git repository (either
`planet-sympy/planet.sympy.org` or `planet-sympy/planet.sympy.org-test`), with
write permissions.

The docker image is periodically pulled and run by GitLab-CI at:
https://gitlab.com/certik/planet-sympy-updater, here is a direct link for the latest builds, so that you can check the status of the latest update of the `planet.sympy.org` website: https://gitlab.com/certik/planet-sympy-updater/pipelines.
