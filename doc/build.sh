#!/bin/sh

rm -r _build
make gettext
sphinx-intl update -p _build/locale
sphinx-intl build
make -e SPHINXOPTS="-D language='ja'" html
mv _build/html _html-ja
make html
mv _html-ja _build/html-ja
