# Sources for planet.sympy.org

## Adding a new blog

Add a new blog a the end of `planet/planetsympy/config`. Send a PR against this
repository. Travis tests must pass: Travis will build a docker image and pull
all the blogs. This will ensure that the syntax in the `config` file is
correct.

# Development

## Build docker image

    docker build -t username/planet-sympy:v1 .

## Run docker image

    docker run -d -e SSH_PRIVATE_KEY=XXX test/planet-sympy:v1

Where you change `XXX` for a base64 encoded private ssh key. This command will
update the planet and push the new files into the
https://github.com/planet-sympy/planet.sympy.org repository.
