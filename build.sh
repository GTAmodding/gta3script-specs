#!/bin/sh
pandoc --toc --standalone -M title="GTA3script Specification" --number-sections --css=pandoc.css core/*.md -o core.html
