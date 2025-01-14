from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sagemaker_studio",
    version="0.0.1",
    author="Amazon Web Services",
    url="https://aws.amazon.com/sagemaker/",
    description="Python library to interact with Amazon SageMaker Unified Studio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    packages=find_packages(),
    python_requires=">=3.11",
    platforms="Linux, Mac OS X, Windows",
    keywords=["AWS", "Amazon", "SageMaker", "SageMaker Unified Studio", "SDK"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
    ],
    install_requires=[
    ]
)
