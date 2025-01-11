from setuptools import setup, find_packages

setup(
    name="SoyleApp",
    version="1.1.0", 
    description="A Python library for interacting with the Soyle Translation API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dari4ok", 
    author_email="Dari4ok.vsl@gmail.com", 
    url="https://github.com/Dari4ok/SoyleApp", 
    license="MIT", 
    packages=find_packages(),
    install_requires=[
        "requests",  
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
