# CadQuery Dockerfile
#
# Takes a Python script using the CadQuery module,
# and outputs a json representation of the 3d model that can be imported in a viewer.
#
# We recommend to run the container in background in order to reduce response time.
# Inspired from the jupyter-cadquery Dockerfile.
#
# Usage:
# 1. docker build docker -t cadquery
# 2. docker run --rm -d --name cq cadquery
# 3. docker exec -i cq python - < my_script.py

FROM continuumio/miniconda3:4.10.3

RUN adduser --disabled-password --gecos "Default user" --uid 1000 cq && \
    apt-get update -y && \
    apt-get install --no-install-recommends -y libgl1-mesa-glx libglu1-mesa && \
    apt-get clean

RUN conda create -n cq -c default -c conda-forge -c cadquery python=3.8 cadquery=master && \
    conda clean --all && \
    find / -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

RUN . "/opt/conda/etc/profile.d/conda.sh" && conda activate cq && \
    pip install jupyter-cadquery==3.0.0 cadquery-massembly~=0.9 matplotlib==3.3 && \
    find / -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

WORKDIR /home/cq
USER cq
ENV PATH="/opt/conda/envs/cq/bin:${PATH}"

CMD tail -f /dev/null
