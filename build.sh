#!/bin/bash

set -e
set -x

# Clean any previous build
rm -rf build
mkdir -p build

# Copy CSS and images from the gh-pages branch if available
if [ -d "tmp/sympy-planet-gh-pages/images" ]; then
  mkdir -p build/images
  cp -R tmp/sympy-planet-gh-pages/images/* build/images/
  echo "Copied images from gh-pages branch"
fi

if [ -f "tmp/sympy-planet-gh-pages/planet.css" ]; then
  cp tmp/sympy-planet-gh-pages/planet.css build/
  echo "Copied CSS from gh-pages branch"
fi

# Generate bootstrap.css and main.css placeholders if they don't exist
touch build/bootstrap.css
touch build/main.css

# Run planet.py to generate the website directly into the build directory
echo "Running planet.py"
./planet.py -d planet/planetsympy/ --update --write --output-dir build

echo "Build completed: website files are in the build directory"