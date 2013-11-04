#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="eos-shell-content"

(test -f $srcdir/unzip_content.py) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level $PKG_NAME directory"
    exit 1
}

which gnome-autogen.sh || {
    echo "You need to install the gnome-common package."
    exit 1
}

USE_GNOME2_MACROS=1 . gnome-autogen.sh
