from setuptools import setup, find_packages
from pathlib import Path

# Ensure the correct file path for your README.rst
long_description = (Path(__file__).parent / 'README.rst').read_text()

setup(
    name="livescraper",  # Package name
    version="1.3.0",   # Version
    packages=find_packages(),  # Automatically find all modules
    install_requires=["requests"],  # List of dependencies
    author="livescraper",
    author_email="livescraper@gmail.com",
    license='MIT',
    description="Python bindings for the Livescraper API",
     long_description=long_description,
    long_description_content_type='text/x-rst',
    url="",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        "Development Status :: 5 - Production/Stable",
    ],
    keywords='livescraper webscraper extractor google api maps search json scrape parser reviews google play',
    python_requires=">=3.6",
)
