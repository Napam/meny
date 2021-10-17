# !/usr/bin/env bash
docker run \
--rm \
-it \
--name meny-container \
--volume $(pwd):/project/meny \
meny-image sh -c "pip install -e meny && sh"