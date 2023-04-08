FROM python:3.10.2-slim

ENV SRCDIR=""

RUN pip install pika==1.3.1 Pillow==9.5.0 PyYaml==6.0

ENV PYTHONUNBUFFERED=1

COPY get_images.py ./get_images.py

CMD python get_images.py ${SRCDIR}
