from setuptools import setup, find_packages
import os

# Читаем README.md если он существует
long_description = ''
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="pyrobby",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pillow",
    ],
    author="Aliaksei Ivanko",
    author_email="your.email@example.com",
    description="A library for controlling a robot in a grid environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyrobby",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_data={
        'robotlib': ['icons/*.png'],
    },
) 