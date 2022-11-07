#!/usr/bin/env bash

HASH_SUM=`./docker/check_enviroment_changes.sh`
CONTAINER=odykusha/blog:${HASH_SUM}

build_dir=$(mktemp -d)

cp -v docker/Dockerfile $build_dir
cp -v docker/packages.txt $build_dir
cp -v docker/requirements.txt $build_dir

cd $build_dir


docker build -f ./Dockerfile -t $CONTAINER .

rm -r $build_dir
