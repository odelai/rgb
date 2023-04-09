import sys
import os
import pika
import logging
import logging.config
import yaml
import shutil

# names of subfolders
RGB = ["red", "green", "blue"]
# inactivity timeout (in seconds)
TIMEOUT: float = 10


def setup_logger() -> logging.Logger:
    with open('/logs/log.yml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    logging.config.dictConfig(config)
    logger = logging.getLogger("PUT_IMAGES")
    return logger


def main():
    amqp_url = os.environ["AMQP_URL"]
    amqp_url_params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(amqp_url_params)
    channel = connection.channel()

    dest_dir = sys.argv[1]
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir, mode=777)

    # queue is declared in both sender(dominant_rgb.py) 
    # and receiver(put_image.py), we do not know whether 
    # sender runs before receiver.
    queuename = "dominant_rgb_queue"
    channel.queue_declare(queue=queuename)
    
    logger = setup_logger()
    
    for _, _, body in channel.consume(queue=queuename):
        if body is None:
            break
        
        body = body.decode()
        threshold = len(body) - 1
        index = int(body[threshold:])
        src_path = body[:threshold]
        
        dest_path = f"{dest_dir}/{RGB[index]}/" 
        
        if not os.path.isdir(dest_path):
            os.mkdir(dest_path, mode=777)
        
        basename = os.path.basename(src_path)
        dest_path += basename
        
        shutil.copyfile(src_path, dest_path)
        
        logger.info(f" [x] Moved image {src_path} to directory {dest_path}")

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