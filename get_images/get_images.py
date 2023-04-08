#!/usr/bin/env python
import sys
import os
import pika
import logging
import logging.config
import yaml
from PIL import Image
from io import BytesIO
from typing import List

# supported formats
FORMATS = tuple(['gif', 'pbm', 'pgm', 'ppm', 'tiff',
           'xbm', 'jpeg', 'bmp', 'png', 'webp', 'exr', 'jpg', 'jfif'])


def setup_logger() -> logging.Logger:
    with open('/logs/log.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    logging.config.dictConfig(config)
    logger = logging.getLogger("GET_IMAGES")
    return logger


def is_valid_args(args: List[str], logger: logging.Logger) -> bool:
    param_len = len(args) - 1
    
    if param_len == 0:
        logger.error("no parameters passed")
        return False
    
    if param_len > 2:
        logger.error(f"too many parameters passed, no more than 2 needed, provided {param_len}")
        return False
        
    dirname = args[1]
    if not os.path.isdir(dirname):
        logger.error(f"invalid directory name: {dirname}")
        return False
    
    return True 


def send_images_to_queue(channel, dirname, logger):
    """Sends images from the directory to the queue

    Args:
        channel (_type_): pika.Channel, established RabbitMQ channel using pika library
        dirname (str): valid directory string
        logger  (logging.Logger)
    """
    
    queuename = "image_queue"
    
    channel.queue_declare(queue=queuename)
    logger.info(f" [x] Created queue: {queuename}")
    
    for file in os.scandir(dirname):
        # ignores not supported formats
        if not file.name.lower().endswith(FORMATS):
            logger.info(f" [*] {file.path} ignored")
            continue
        
        with Image.open(file.path) as image:
            # image is sent as bytes 
            byte_imgIO = BytesIO()
            image.save(byte_imgIO, image.format)
            byte_imgIO.seek(0)
            image = byte_imgIO.read()
            
            # longest path can only be 256 characters long
            filename_with_path = file.path.ljust(256, " ").encode()
            body = image + filename_with_path
            
            channel.basic_publish(exchange='',
                                  routing_key=queuename,
                                  body=body)
            
            logger.info(f" [x] Sent image: {file.path} to {queuename}")


def main():  
    logger = setup_logger()  
    
    if not is_valid_args(sys.argv, logger):
        sys.exit(1)
    
    dirname = sys.argv[1]
    
    amqp_url = os.environ['AMQP_URL']
    amqp_url_params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(amqp_url_params)
    channel = connection.channel()

    send_images_to_queue(channel, dirname, logger)
    
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
