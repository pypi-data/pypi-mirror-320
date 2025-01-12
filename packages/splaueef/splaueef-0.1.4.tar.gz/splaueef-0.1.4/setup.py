from setuptools import setup, find_packages

# Налаштування бібліотеки
setup(
    name="splaueef",
    version="0.1.4",
    packages=find_packages(),
    install_requires=["aiogram>=3.0", "certifi"],
    author="Splaueef",
    author_email="Splaueef@gmail.com",
    description="Допоміжна бібліотека для роботи з aiogram",
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
            "splaueef-init=splaueef:init_project",
        ],
    },
)