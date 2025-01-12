from setuptools import setup, find_packages
from os import path

from setuptools.config.expand import entry_points

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='GIMPy_Widget_UI',
    version='0.1.1',
    # url='https://github.com/',
    author='Manish Kathuria',
    author_email='gimpywidgetui@gmail.com',
    description='Python classes supporting use of GUI created in GIMP',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['asttokens', 'pillow', 'opencv-python', 'numpy'],
    entry_points={'console_scripts': ['map_gimpy = GIMPy_Widget_UI:map_gimpy', ], },
)