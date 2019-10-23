#!/usr/bin/env bash

nvidia-docker run --rm -it -p "8888:8888" \
-v `pwd`/../../aws-deepracer-workshops/log-analysis:/workspace/venv/data \
-v `pwd`/../../docker/volumes/.aws:/root/.aws \
-v `pwd`/../../docker/volumes/robo/checkpoint/log:/workspace/venv/logs \
  wirawan/deepracer-log-analysis
