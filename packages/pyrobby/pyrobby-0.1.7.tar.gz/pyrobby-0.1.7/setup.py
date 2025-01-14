from setuptools import setup, find_packages
import os

# Читаем README.md если он существует
long_description = ''
if os.path.exists('README.md'):
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="pyrobby",
    version="0.1.7",
    packages=['robot'],
    include_package_data=True,
    package_data={
        'robot': [
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
        ('robot/icons', [
            'robot/icons/robot.png',
            'robot/icons/new_tab.png',
            'robot/icons/close_tab.png',
            'robot/icons/save.png',
            'robot/icons/open.png',
            'robot/icons/start.png',
            'robot/icons/end.png',
            'robot/icons/return.png',
            'robot/icons/restore.png',
            'robot/icons/reset.png',
            'robot/icons/remote-control.png'
        ])
    ],
    install_requires=[
        "pillow>=10.0.0",
        "tk",
        "setuptools>=42.0.0",
        "wheel>=0.37.0",
    ],
    python_requires='>=3.6',
    author="Aliaksei Ivanko",
    author_email="your.email@example.com",
    description="A library for controlling a robot in a grid environment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyrobby",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 