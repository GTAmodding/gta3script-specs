#!/bin/bash
set -e
git clone https://github.com/gtamodding/gta3script-specs.git /tmp/gta3script-specs
cd /tmp/gta3script-specs
./build.sh
git checkout gh-pages
git add *.html
git commit -m "Deploy"
git push origin gh-pages
cd /tmp && rm -rf gta3script-specs
