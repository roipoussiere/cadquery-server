FROM python:3.9

RUN pip install 'cadquery-server[cadquery]'

RUN apt-get update && apt-get install -y \
	libgl1 \
	libgl1-mesa-glx \
	&& rm -rf /var/lib/apt/lists/*

RUN mkdir /data
WORKDIR data

RUN echo "import cadquery as cq\nfrom cq_server.ui import UI, show_object\nshow_object(cq.Workplane().box(10,10,10))" > /data/main.py

ENTRYPOINT ["cq-server", "/data"]
