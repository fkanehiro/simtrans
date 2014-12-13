This folder contains documentation for simtrans

To generate the document:

$ sudo pip install -r requires.txt
$ ./build.sh

html document will be generated under _build/html and _build/html-ja

To update the document:

- Edit *.rst file (in English)

- Generate gettext pot file and update the translation data
$ make gettext
$ sphinx-intl update -p _build/locale

- Edit translation file generated under locale/ja/LC_MESSAGES

You can use any editor to edit po file but my recommendation is "poedit".
