#!/bin/bash

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

build_html()
{
    asciidoctor $1 -o $2 -v -a linkcss -a docinfo=shared-head -a docinfodir=$BASEDIR -r "$BASEDIR/tools/asciidoctor-grammar-preprocessor.rb"
}

build_html "$BASEDIR/core/index.adoc" "$BASEDIR/core.html"
build_html "$BASEDIR/dma/gta3/index.adoc" "$BASEDIR/dma/gta3.html"
build_html "$BASEDIR/index.adoc" "$BASEDIR/index.html"
