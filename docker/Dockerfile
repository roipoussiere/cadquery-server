# CadQuery server Dockerfile based on Flask, inspired by the jupyter-cadquery Dockerfile.
#
# Basic usage:
# 1. docker build docker -t cadquery
# 2. docker run --rm -d --name cq -p 5000:5000 cadquery
# 3. curl -X POST --data-binary "@./examples/test.py" 127.0.0.1:5000

FROM continuumio/miniconda3:4.10.3

RUN adduser --disabled-password --gecos "Default user" --uid 1000 cq && \
    apt-get update -y && \
    apt-get install --no-install-recommends -y libgl1-mesa-glx libglu1-mesa && \
    apt-get clean

RUN conda create -n cq -c default -c conda-forge -c cadquery python=3.8 cadquery=master && \
    conda clean --all && \
    find / -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

RUN . "/opt/conda/etc/profile.d/conda.sh" && \
    conda activate cq && \
    pip install cadquery-server && \
    find / -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

WORKDIR /home/cq
USER cq

ENV PATH="/opt/conda/envs/cq/bin:${PATH}"

CMD cq-server
