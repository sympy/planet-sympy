#!/bin/bash

set -e
set -x

mkdir -p build
cp -R planet/* build/

# Copy CSS and images from the gh-pages branch if available
if [ -d "tmp/sympy-planet-gh-pages/images" ]; then
  mkdir -p build/planetsympy/website/images
  cp -R tmp/sympy-planet-gh-pages/images/* build/planetsympy/website/images/
  echo "Copied images from gh-pages branch"
fi

if [ -f "tmp/sympy-planet-gh-pages/planet.css" ]; then
  cp tmp/sympy-planet-gh-pages/planet.css build/planetsympy/website/
  echo "Copied CSS from gh-pages branch"
fi

# Generate bootstrap.css and main.css placeholders if they don't exist
touch build/planetsympy/website/bootstrap.css
touch build/planetsympy/website/main.css

# Using our new planet.py instead of rawdog
cd build
echo "Running planet.py"
../planet.py -d planetsympy/ --update --write