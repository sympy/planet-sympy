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

This repository is automatically deployed as follows.

First, a docker image from the latest master is automatically built by
GitLab-CI and made available at:
https://gitlab.com/sympy/planet-sympy/container_registry. This is achieved by
having a GitLab [mirror](https://gitlab.com/sympy/planet-sympy) automatically
running a pipeline from the master branch updating the docker image whenever it
changes.

Second, we have a repository at https://gitlab.com/sympy/planet-sympy-updater,
which has a pipeline that takes the latest docker image and runs it. This
pipeline is triggered via a cron script every 20 minutes. Here is a direct link
for the latest builds, so that you can check the status of the latest update of
the `planet.sympy.org` website:
https://gitlab.com/sympy/planet-sympy-updater/pipelines.

Third, when the docker image is run, it will update the planet and push the new
files into the https://github.com/planet-sympy/planet.sympy.org repository.
