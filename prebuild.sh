#!/bin/bash -xe

build_dl "https://dl.fedoraproject.org/pub/epel/epel-release-latest-$DIST_VERSION.noarch.rpm"
rpm -Uvh "$CACHEDIR/epel-release-latest-$DIST_VERSION.noarch.rpm"

if [[ $DIST == el8 ]]; then
    build_dl "https://dl.fedoraproject.org/pub/epel/epel-next-release-latest-$DIST_VERSION.noarch.rpm"
    rpm -Uvh "$CACHEDIR/epel-next-release-latest-$DIST_VERSION.noarch.rpm"
fi
