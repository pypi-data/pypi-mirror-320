from setuptools import setup, find_packages
import os

# Читаем README.md если он существует
long_description = ''
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="pyrobby",
    version="0.1.2",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'robotlib': [
            'icons/*.png',
            'icons/robot.png',
            'icons/new_tab.png',
            'icons/close_tab.png',
            'icons/save.png',
            'icons/open.png',
            'icons/start.png',
            'icons/end.png',
            'icons/return.png',
            'icons/restore.png',
            'icons/reset.png',
            'icons/remote-control.png'
        ],
    },
    data_files=[
        ('robotlib/icons', [
            'robotlib/icons/robot.png',
            'robotlib/icons/new_tab.png',
            'robotlib/icons/close_tab.png',
            'robotlib/icons/save.png',
            'robotlib/icons/open.png',
            'robotlib/icons/start.png',
            'robotlib/icons/end.png',
            'robotlib/icons/return.png',
            'robotlib/icons/restore.png',
            'robotlib/icons/reset.png',
            'robotlib/icons/remote-control.png'
        ])
    ],
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
) 