from setuptools import setup, find_packages

setup(
    name="IndiSynth",
    version="1.0.3",
    author="Sai Raam",
    author_email="srinrealyf@gmail.com",
    description="A comprehensive synthetic data generator for Indian entities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/srinrealyf/indisynth",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="Apache License 2.0"
)
