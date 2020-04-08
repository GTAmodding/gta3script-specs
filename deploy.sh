#!/bin/bash
set -e
git clone https://github.com/gtamodding/gta3script-specs.git /tmp/gta3script-specs
cd /tmp/gta3script-specs
./build.sh
git checkout gh-pages
find . -type f \( -name '*.html' -or -name '*.css' \) -exec git add {} \;
git rm docinfo.html
git commit -m "Deploy"
git push origin gh-pages
cd /tmp && rm -rf gta3script-specs
