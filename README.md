# rgb

Mini python application that sorts images based on dominant rgb channel. Consists of 3 modules:

1. loads image data into system
2. defines the dominant RGB channel
3. saves individual images into corresponding subfolders.

Each module runs as a separate docker container and combined together with docker compose.
Modules communicate with each other via RabbitMQ message broker.

## Run the program

Commands to run the program (and docker-compose.yml) use UNIX paths (paths have '/' divisor unlike in Windows and export 
commands are the shell commands).

* export the source directory as a variable: `export SRCDIR=<path_to_directory>`
* export target directory variable: `export DESTDIR=<path_to_directory>` (optional, by default is "output_dir")
* build: `docker-compose build`
* run: `docker-compose up`
* to clean up use:  `docker-compose down -v --rmi all --remove-orphans`
* We can run separate containers: `docker-compose up <container_name>` (container_names: get-images, dominant-rgb, put-images, unit-tests)

It doesn't move the images, but only copies to the target directory (to red, green or blue subfolder correspondingly)
However, resulting images have limited permssion mode, so run `sudo chmod 400 .` after getting in each subfolder (`cd <dest_dir/channel>`).


