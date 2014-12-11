#!/bin/sh

sphinx-intl update -p _build/locale
sphinx-intl build
make -e SPHINXOPTS="-D language='ja'" html
