#!/usr/bin/env python
import sys
import os
import pika
import logging
import logging.config
import yaml
from PIL import Image
import numpy as np
import io

TIMEOUT: float = 5

def setup_logger() -> logging.Logger:
    with open('/logs/log.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    logging.config.dictConfig(config)
    logger = logging.getLogger("DOMINANT_RGB")
    return logger
    

def get_dominant_rgb(image: Image) -> int:
    """
    Returns index representing the dominant rgb channel of the image.
    red: 0,
    green: 1,
    blue: 2.
    
    """
    channels = image.split()
    
    means = list(map(np.mean, channels))[:3]
    return np.argmax(means)       

def main():
    amqp_url = os.environ["AMQP_URL"]
    url_params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(url_params)
    channel = connection.channel()
    
    # queue is declared in both sender(get_images.py) 
    # and receiver(dominant_rgb.py), we do not know whether 
    # sender runs before receiver.
    receive_queuename = "image_queue"
    channel.queue_declare(queue=receive_queuename)
    
    send_queuename = "dominant_rgb_queue" 
    channel.queue_declare(queue="dominant_rgb_queue")

    logger = setup_logger()

    for _, _, body in channel.consume(queue=receive_queuename):
        if body is None:
            break
        
        threshold = len(body) - 256
        path = body[threshold:].decode().strip()

        body = body[:threshold]
        img = Image.open(io.BytesIO(body))
        
        channel.basic_publish(exchange='',
                              routing_key=send_queuename,
                              body=path.encode() + bytes(str(get_dominant_rgb(img)), 'utf-8'))        
        
        logger.info(f" [x] Received image {path} from {receive_queuename}")
        logger.info(f" [x] Sent image {path} to {send_queuename}")
    
    channel.close()
    connection.close()
    
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)