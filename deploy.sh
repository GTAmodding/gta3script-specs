#!/bin/bash
set -e
git clone https://github.com/gtamodding/gta3script-specs.git /tmp/gta3script-specs
cd /tmp/gta3script-specs
./build.sh
mkdir build
cp *.html build/
cp *.css build/
git checkout gh-pages
cp build/*.html ./
cp build/*.css ./
rm -r build
git add *.html *.css
git commit -m "Deploy"
git push origin gh-pages
cd /tmp && rm -rf gta3script-specs
