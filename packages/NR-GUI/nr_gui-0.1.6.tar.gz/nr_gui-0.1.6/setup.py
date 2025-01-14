from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))



VERSION = '0.1.6'
DESCRIPTION = 'Simple gui package, you can use it for easy gui'


# Setting up
setup(
    name="NR_GUI",
    version=VERSION,
    author="NR_5tudio",

    description=DESCRIPTION,


    packages=find_packages(),
    install_requires=['gdown'],
    keywords=['python', 'tkinter', 'EZ_GUI', 'GUI', 'NR', 'NR_5tudio'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)