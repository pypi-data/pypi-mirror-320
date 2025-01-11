from setuptools import setup, find_packages

setup(
    name="getscraper",  # Package name
    version="0.4.0",   # Version
    packages=find_packages(),  # Automatically find all modules
    install_requires=[],  # List of dependencies
    author="Your Name",
    author_email="",
    description="A demo package for greeting users",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
