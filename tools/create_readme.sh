#!/bin/sh

make -C doc text
cp -f doc/_build/text/overview.txt README.txt
