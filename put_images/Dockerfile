FROM python:3.10.2-slim

ENV DESTDIR="/output_dir"

RUN pip install pika==1.3.1 PyYaml==6.0

ENV PYTHONUNBUFFERED=1

COPY put_images.py ./put_images.py

CMD python put_images.py ${DESTDIR}
