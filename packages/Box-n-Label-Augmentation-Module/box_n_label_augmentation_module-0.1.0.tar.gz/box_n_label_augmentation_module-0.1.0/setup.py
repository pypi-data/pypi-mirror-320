from setuptools import setup, find_packages

setup(
    name="Box-n-Label-Augmentation-Module",  
    version="0.1.0",
    author="MHosseinHashemi",
    author_email="lasteurus8@gmail.com",
    description="Custom data augmentation module for images and bounding boxes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MHosseinHashemi/Box-n-Label-Augmentation-Module", 
    packages=find_packages(),
    install_requires=open("C:\\Users\\laste\\Desktop\\Test The Module\\Box-n-Label-Augmentation-Module\\requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9.7",
)
