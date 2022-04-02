# CadQuery server Dockerfile based on Flask, inspired by the jupyter-cadquery Dockerfile.
#
# Basic usage:
# 1. docker build docker -t cadquery
# 2. docker run --rm -d --name cq -p 5000:5000 cadquery
# 3. curl -X POST --data-binary "@./examples/test.py" 127.0.0.1:5000

FROM cadquery/cadquery

USER root
RUN pip install cadquery-server

USER cq
WORKDIR /home/cq

CMD cq-server
