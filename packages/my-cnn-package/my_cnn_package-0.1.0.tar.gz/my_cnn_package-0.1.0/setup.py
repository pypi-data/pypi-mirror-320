from setuptools import setup, find_packages

setup(
    name="my_cnn_package",
    version="0.1.0",
    description="A simple PyTorch CNN package",
    author="Cuong Van",
    packages=find_packages(),
    install_requires=[
        "torch>=1.10.0",
        "torchvision>=0.11.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
