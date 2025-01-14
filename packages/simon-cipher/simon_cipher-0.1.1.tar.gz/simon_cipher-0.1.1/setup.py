# setup.py
from setuptools import setup, find_packages

setup(
    name="simon_cipher",
    version="0.1.1",
    description="Python implementation of the Simon cipher",
    author="Azaliya",
    author_email="azakhabi19@gmail.com",
    packages=find_packages(),
    install_requires=[],  # Здесь можно указать зависимости, если они есть
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Минимальная версия Python
)
