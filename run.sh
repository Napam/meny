# !/usr/bin/env bash
docker run \
--rm \
-it \
--name pypatconsole-container \
--volume $(pwd):/project/pypatconsole \
pypatconsole-image sh -c "pip install -e pypatconsole && sh"