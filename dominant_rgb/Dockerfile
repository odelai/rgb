FROM python:3.10.2-slim

RUN pip install numpy==1.22.1 pika==1.3.1 Pillow==9.5.0 PyYaml==6.0

ENV PYTHONUNBUFFERED=1

COPY dominant_rgb.py ./dominant_rgb.py

CMD  python dominant_rgb.py
