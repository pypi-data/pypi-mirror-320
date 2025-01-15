from setuptools import setup, find_packages
import pathlib

setup(
    name='fbrefstats',
    version='0.1.0',    
    description='A Python script to scrape football data from FBRef',
    url='https://github.com/mbrahimi25/fbrefstats',
    author='Mohamed Brahimi',
    license='GNU GPL v2',
    install_requires=['requests', 'pandas', 'bs4', 'fake_http_header', 'io'],

    classifiers = [
    	"Programming Language :: Python :: 3",
    	"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    	"Operating System :: OS Independent",
    ]
)