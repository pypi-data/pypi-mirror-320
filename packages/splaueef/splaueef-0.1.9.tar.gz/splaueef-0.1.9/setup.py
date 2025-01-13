# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.install import install


setup(
    name="splaueef",
    version="0.1.9",
    packages=find_packages(),
    install_requires=[
        "aiogram>=3.0",
        "certifi",
        "pyzbar",
        "pytesseract",
        "pillow",
        "aiosqlite",
    ],
    author="Splaueef",
    author_email="Splaueef@gmail.com",
    description="Helper library for working with aiogram, including tools for creating keyboards, handling commands, image processing, and database management.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Splaueef/aiohelp.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "splaueef-init=splaueef.utils:init_project",
        ],
    },
)
