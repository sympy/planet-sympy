# Sources for planet.sympy.org

## Adding a new blog

Add a new blog a the end of `planet/planetsympy/config`. Send a PR against this
repository. Travis tests must pass: Travis will build a docker image and pull
all the blogs. This will ensure that the syntax in the `config` file is
correct.

# Development

## Build docker image

    docker build -t username/sympy-paper:v1 .

## Run docker image

    docker run -it username/sympy-paper:v1
