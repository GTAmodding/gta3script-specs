#!/bin/sh
asciidoctor -a linkcss -a docinfo=shared-head -a docinfodir="$(pwd)" core/index.adoc -o core.html
