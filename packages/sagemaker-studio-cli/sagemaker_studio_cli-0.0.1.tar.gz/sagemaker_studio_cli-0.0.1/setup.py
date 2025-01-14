from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="sagemaker_studio_cli",
    version="0.0.1",
    author="Amazon Web Services",
    description="CLI to interact with SageMaker Studio",
    url="https://aws.amazon.com/sagemaker/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[],
    license="Apache License 2.0",
    platforms="Linux, Mac OS X, Windows",
    keywords=["AWS", "Amazon", "SageMaker", "SageMaker Unified Studio", "CLI"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
    ],
)
