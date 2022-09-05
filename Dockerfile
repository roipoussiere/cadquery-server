FROM python:3.9

RUN apt-get update && apt-get install -y \
	libgl1 \
	libgl1-mesa-glx \
	git \
	&& rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/roipoussiere/cadquery-server.git \
	&& cd cadquery-server \
	&& pip install '.[cadquery]'

VOLUME ["data"]
WORKDIR data


ENTRYPOINT ["cq-server"]
