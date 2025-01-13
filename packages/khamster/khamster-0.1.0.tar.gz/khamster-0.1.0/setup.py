from setuptools import setup, find_packages

setup(
    name="khamster",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "roboid>=1.4.0"
    ],
    author="Andrea",
    author_email="",
    description="A Python package called khamster",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
