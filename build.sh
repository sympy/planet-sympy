#!/bin/bash

set -e
set -x

# Clean any previous build
rm -rf build
mkdir -p build

# Create necessary directories
mkdir -p build/images
mkdir -p build/hackergotchi
mkdir -p build/js
mkdir -p build/fonts

# Copy resources from the website directory
if [ -d "planet/website/images" ]; then
  cp -R planet/website/images/* build/images/ 2>/dev/null || true
  echo "Copied images from website directory"
fi

if [ -d "planet/website/hackergotchi" ]; then
  cp -R planet/website/hackergotchi/* build/hackergotchi/ 2>/dev/null || true
  echo "Copied hackergotchi from website directory"
fi

if [ -d "planet/website/js" ]; then
  cp -R planet/website/js/* build/js/ 2>/dev/null || true
  echo "Copied JS from website directory"
fi

if [ -d "planet/website/fonts" ]; then
  cp -R planet/website/fonts/* build/fonts/ 2>/dev/null || true
  echo "Copied fonts from website directory"
fi

if [ -d "planet/website/css" ]; then
  cp planet/website/css/bootstrap.css build/ 2>/dev/null || true
  cp planet/website/css/main.css build/ 2>/dev/null || true
  echo "Copied CSS from website directory"
fi

# Fallback to copying from gh-pages branch if needed images aren't available
if [ ! -d "planet/website/images" ] && [ -d "tmp/sympy-planet-gh-pages/images" ]; then
  cp -R tmp/sympy-planet-gh-pages/images/* build/images/ 2>/dev/null || true
  echo "Copied images from gh-pages branch"
fi

# Run planet.py to generate the website directly into the build directory
echo "Running planet.py"
./planet.py -d planet/planetsympy/ --update --write --output-dir build

echo "Build completed: website files are in the build directory"