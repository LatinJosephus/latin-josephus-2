#!/bin/sh
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update > /out/dependencies.log 2>&1
apt-get install -y --no-install-recommends build-essential pkg-config libmagickwand-dev imagemagick graphviz git >> /out/dependencies.log 2>&1
mkdir -p /work
tar -C /src --exclude=.git --exclude=review --exclude=_site --exclude=.jekyll-cache --exclude=vendor -cf - . | tar -C /work -xf -
gem install bundler -v 4.0.22 --no-document >> /out/dependencies.log 2>&1
cd /work
bundle _4.0.22_ install >> /out/dependencies.log 2>&1
JEKYLL_ENV=development bundle _4.0.22_ exec jekyll build --destination /out/site --trace > /out/jekyll.log 2>&1
