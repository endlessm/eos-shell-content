#!/usr/bin/perl
use warnings;
use strict;
use Debian::Debhelper::Dh_Lib;

# Run before dh_fixperms so that installed files are
# completely settled before fixing permissions.
insert_before("dh_fixperms", "dh_eoscontent");

1;
