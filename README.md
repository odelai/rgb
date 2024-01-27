# rgb

Mini python application that sorts images based on dominant rgb channel. Consists of 3 modules:

1. loads image data into system
2. defines the dominant RGB channel
3. saves individual images into corresponding subfolders.

Each module runs as a separate docker container and combined together with docker compose.
Modules communicate with each other via RabbitMQ message broker.

## Run the program

Commands to run the program (and docker-compose.yml) use UNIX paths (paths have '/' divisor unlike in Windows), export and chmod commands are the shell commands).

* export the source directory as a variable: `export SRCDIR=<path_to_directory>` (you can try ./example_dir as the <path_to_directory>)
* export target directory variable: `export DESTDIR=<path_to_directory>` (optional, by default is "output_dir")
* build: `docker-compose build` or if using sudo: `sudo -E docker-compose build`
* run: `docker-compose up` or `sudo -E docker-compose up` (-E if a short form of --preserve-env and it tells security policy to preserve existing environment variables, i.e. our SRCDIR variable as well.)
* to clean up use:  `docker-compose down -v --rmi all --remove-orphans`
* We can run separate containers: `docker-compose up <container_name>` or `sudo -E docker-compose up <container_name>`(container_names: get-images, dominant-rgb, put-  images, unit-tests)

It doesn't move the images, but only copies to the target directory (to red, green or blue subfolder correspondingly).

However, resulting folder might have permssion issues, so you can run `sudo chmod -R 777 <target_directory>`.

Supported formats: jpg, png, jfif, pbm, xbm, pgm, ppm, tiff, webp, bmp.



This project provides the set of tools for correcting cell segmentation results using the sample datasets from Cell
Tracking Challenge. Toolset prepares the data for Tomviz, and after that performs postprocessing.  

# Directory structure

Directory structure:
```
datasets/
├── DIC-C2DH-HeLa/
├── Fluo-N2DH-GOWT1/
└── Fluo-N2DL-HeLa/

modified/
├── inheritance/
├── label/
├── open/
├── result/
├── stretch/
└── videos/

Fluo-N2DH-GOWT1/
├── 01/
├── 01_GT/
│   ├── SEG/
│   └── TRA/
├── 01_ST/
│   └── SEG/
├── 02/
├── 02_GT/
│   ├── SEG/
│   └── TRA/
└── 02_ST/
    └── SEG/
```

The initial datasets are stored in 'datasets' directory. Each of the dataset has the same structure containing original images, golden truths(GT), and silver truths(ST). This project deals with silver truth segmentation results. 
Scripts work on copies of the data and stor save them in modified/.

# Scripts

```
Name: inheritance.py
Description: preserves the inheritance. Cell with all its descendants are labeled the same. This way, only primary labels remain.
Usage: python inheritance.py <src> <dst> <inher>
Arguments:
	<src> 		Source directory
	<dst> 		Destination directory
	<inher>		Filename with path where the inheritance file is stored

Additionaly, it prints out relevant inheritance data. Example for Fluo-N2DH-GOWT1:

Total amount of all labels: 29
Total amount of primary labels: 24
Primary labels: [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]

Labels with the most descendants: [10, 16]
Number of descendants: 2
```

```
Name: label.py
Description: Filters out all other label except the given one. It produces binary image, background becomes 0, foreground(labels) becomes 1.
Usage: python label.py <src> <dst> <label>
Arguments:
	<src>		Source directory
	<dst> 		Destination directory
	<label> 	Label value to keep, if 0 then keeping all the labels
```


```
Name: custom_binary_open.py
Description: Performs morphological binary opening on segmented objects by a 3d bar structuring element with a given depth.
Usage: This script is not used via command line, but passed to tomviz and launched using its graphical interface.
```

```
Name: custom_binary_close.py
Description: Performs morphological binary closing on segmented objects by a 3d bar structuring element with a given depth.
Usage: This script is not used via command line, but passed to tomviz and launched using its graphical interface.
```

```
Name: bring_back.py
Description: Splits the multitiff image produced by Tomviz into individual images. Assigns back all the labels as it was in the segmentation result(i.e. without inheritance). And since binary opening might cover pixels that were not initially part of it, it compares result with the original dataset.
Usage: python bring_back.py <src> <dst> <origin>
Arguments:
	<src> 		Source to multitiff file
	<dst> 		Destination directory
	<origin>	Directory where the original segmentation results are stored
```

```
Name: connected_components.py
Description: filters out artifacts computing connected components and discarding those that are below a given threshold
Usage: python connected_components.py <src> <dst> <threshold>
Arguments:
	<src> 		Source directory
	<dst> 		Destination directory
	<threshold> Areas of components that are below this threshold are discarded
```

```
Name: iou.py
Description: Computes intersection-over-unit. 
Usage: python iou.py <src> <initial_dataset>
Arguments:  
	<src>				Source directory
	<intial_dataset>	Directory of initial dataset, in our case silver segmentation truth 
```

```
Name: recall.py
Description: Computes recall. 
Usage: Usage: python recall.py <src> <tra>
Arguments:  
	<src>		Source directory
	<tra>		Directory of golden tracking truth 
```

```
Name: make_video
Description: Makes video from the sequence of images. It is not part of the workflow, however might be useful. 
Usage: python make_video.py <src> <dst> <fps>
Arguments:
	<src>		Source directory
	<dst>		Destination directory
	<fps>		Frames per second
```

```
Name: stretch.py
Description: Does the linear stretching of intensities. Also serves just as helping script.
Usage: python stretch.py <src> <dst> <lower>
Arguments:	
	<src>		Source directory
	<dst>		Destination directory
	<lower>		Value of lower boundary
```

# Example

One of the possible worflows can be as follows:

    1. python inheritance.py datasets/<dataset_name>/01_ST/SEG/  modified/inheritance/<dataset_name>/  datasets/<dataset_name>/01_GT/TRA/man_track.txt

    2. python label.py modified/inheritance/<dataset_name>/  modified/label/<dataset_name>/ <label>
	
    3. then uploading the data from modified/label/<dataset_name> to Tomviz
	
    4. performing binary opening/closing in Tomviz and saving the data in modified/open/ as one multitiff image
	
    5. python bring_back.py modified/open/<dataset_name>.tiff  modified/result/<dataset_name>/  datasets/<dataset_name>/01_ST/SEG/
	
    6. the resulting images are in datasets/result/<dataset_name>

Pass the name of the dataset in place of <dataset_name>. Insert the examined label in <label>, if you want to keep all then 0.
