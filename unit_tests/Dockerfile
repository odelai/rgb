FROM python:3.10.2-slim

ENV PYTHONUNBUFFERED=1

RUN pip install pika==1.3.1 Pillow==9.5.0 PyYaml==6.0  

COPY test_get_images.py ./test_get_images.py

CMD python -m unittest test_get_images.py