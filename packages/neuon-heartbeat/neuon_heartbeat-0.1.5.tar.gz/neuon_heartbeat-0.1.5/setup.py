# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 18:52:15 2024

@author: yangl
"""

from setuptools import setup, find_packages

setup(
      name="neuon-heartbeat",
      version="0.1.5",
      author="holmes",
      author_email="tidusyuna88@gmail.com",
      description="Generic Heartbeat module using MongoDB as record",
      packages=find_packages(),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      python_requires=">=3.6",
      install_requires=[
        "pymongo>=4.7.3",  
        "neuon>=0.0.1",
        "neuondb>=0.1.0"
      ],
      )
