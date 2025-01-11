# -*- coding: utf-8 -*-
#############################################
# File Name: setup.py
# Author: Yixin Li
# Mail: 20185414@stu.neu.edu.cn
# Created Time:  2025-01-10
#############################################
from setuptools import setup, find_packages



with open("README.md", 'r', encoding='utf-8') as f:
    readme = f.read()


setup(
    name="udmt-pip",
    version="0.0.1",
    description=("UDMT: Unsupervised Multi-animal Tracking for Quantitative Ethology"),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Yixin Li, Xinyang Li",
    author_email="liyixin318@gmail.com",
    url="https://github.com/cabooster/UDMT",
    license="Non-Profit Open Software License 3.0",
    packages=find_packages(),
    install_requires=['matplotlib','pandas','tqdm','pyyaml','tifffile','opencv-python','visdom','tb-nightly','similaritymeasures','torchsummary',
                      'jpeg4py','gdown','pycocotools'],
)
