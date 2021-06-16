#!/usr/bin/sh
SOURCE_DIR=$1

rm docs/source/api/*
rm -r docs/build/html/*

set -e

# re-generating the API documentation from source
# APIDOC_OPTIONS="-d 1 --no-toc --separate --force --private"
# sphinx-apidoc $APIDOC_OPTIONS -o docs/source/generated/ toolbox_drivein
sphinx-apidoc -o docs/source/api/ $SOURCE_DIR

# building the doc
sphinx-build -M html docs/source docs/build

this_dir=$(pwd)
echo "Starting a simple server to show the docs"
echo ""
echo "http://$(hostname).inetpsa.com:10080"
echo ""
cd docs/build/html/
python -m SimpleHTTPServer 10080

cd $this_dir
