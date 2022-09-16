FROM python:3.10

RUN apt-get update && apt-get install -y \
	libgl1 \
	libgl1-mesa-glx \
	&& rm -rf /var/lib/apt/lists/*

# Install project dependencies, without installing the project
COPY pyproject.toml /app/
RUN mkdir /app/cq_server \
	&& touch /app/cq_server/__init__.py \
	&& touch /app/README.md
RUN pip install /app[cadquery]

# Then copy project and install it
# this way pip will not install dependencies each time a change is made on the folder
COPY cq_server /app/cq_server/
RUN rm -rf /app/cq_server/__pycache__
RUN pip install /app[cadquery]

VOLUME ["data"]
WORKDIR data


ENTRYPOINT ["cq-server"]
