#!/usr/bin/perl
use warnings;
use strict;
use Debian::Debhelper::Dh_Lib;

# Run after dh_eosapp so that files are definitely migrated to the
# proper location.
insert_after("dh_eosapp", "dh_eoscontent");

1;
