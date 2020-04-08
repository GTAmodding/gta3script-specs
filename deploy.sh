#!/bin/bash
set -e
git clone https://github.com/gtamodding/gta3script-specs.git /tmp/gta3script-specs
cd /tmp/gta3script-specs
./build.sh
mkdir build build/dma build/extensions
cp *.html *.css build/
git checkout gh-pages
cp build/*.html build/*.css ./
rm -r build docinfo.html
git add .
git commit -m "Deploy"
git push origin gh-pages
cd /tmp && rm -rf gta3script-specs
