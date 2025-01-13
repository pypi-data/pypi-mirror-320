# coding=utf-8

import os
import pathlib
import sys

sys.path.append(os.path.dirname(__file__))
from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

install_requires = [
    "filetype==1.2.0",
    "numpy",
    "onnx==1.15.0",
    "onnxruntime",
    "opencv-python==4.8.1.78",
    "realesrgan==0.3.0",
    "tqdm",
]

extras_require = {
    "gpu": ["onnxruntime-gpu"],
}

setup(
    name="facefusionlib",
    version="1.1.3",
    description="Face swapper and enhancer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IAn2018cs/sd-webui-facefusion",
    author="IAn2018",
    author_email="ian2018cs@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="face, swapper",
    python_requires=">=3.9, <3.13",
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
)
