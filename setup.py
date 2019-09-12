import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easypds4writer",
    version="0.1.0",
    author="Diego Fraga Agudo",
    author_email="dfraga@sciops.esa.int",
    description="Python 3 package to write PDS4 compliant products (both data file and label file). Current prototype supports only products containing fixed width ASCII tables. PDS4 info at https://pds.nasa.gov/datastandards/about/ . This is not an official ESA piece of software.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/esdc-esac-esa-int",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)