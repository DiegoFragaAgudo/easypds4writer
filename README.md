# EasyPDS4writer

Python 3 package to write PDS4 compliant products including both the data file and its label file. For more information about PDS4 standards see https://pds.nasa.gov/datastandards/about/ . 
**Currently the package is a proof of concept or prototype with limited functionality.** At this stage backwards incompatible changes can still occur. Before using it in production please contact its author. Only products containing fixed width ASCII tables (Table_Character object) are supported so far.

## Prerequisites
### Dependencies
This package needs the following common python modules/packages:
- numpy
- ElementTree XML API (xml.etree)

It is pending to create a requirements.txt file.

### Python version
This software has been developed and tested on Python 3.7 therefore Python 3.7 or higher is recommended. However it is believed to work on Python V3.4 or higher.
Python 2.X is not supported.

### OS
The package is Operative System independent.
Development and main testing has been done on Windows whereas some limited testing has been done on Linux/MAC.

## Installation
Download the package and run the provided setup.py in the same way you would run any other Python script in your environment.

### Checking installation
From your systems command line type:

`from easypds4writer.product_observational import ProductObservational`

If it does not return an error then the package is correctly installed and can be found by Python

## Running an example
The package comes with an example in the test directory. Run it as you would run in your system any other python script and it should generate two products in the test/output directory.

## Author
This tool is being developed by Diego Fraga Agudo. It is not an official ESA software. 

Contact email: dfraga@sciops.esa.int

The tool is being developed in a best efforts basis only.

## Acknowledgments
The author would like to thank Mark Bentley for his feedback.

## Want to provide feedback?
You are very welcome, please contact the author. 

I am interesting on help with testing on different platforms and Python versions. Bugs reports, development priorities and ideas are welcome. If you want to contribute with code, please contact the author to discuss about it.

If you are interested as a potential user you are also very welcome to contact the author to show your interest. This is important for the continuity of the project.

