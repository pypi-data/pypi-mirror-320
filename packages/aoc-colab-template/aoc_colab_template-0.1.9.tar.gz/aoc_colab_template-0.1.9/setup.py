from setuptools import setup, find_packages

setup(
    name="aoc-colab-template",
    version="0.1.9",
    packages=find_packages(),
    install_requires=[
        'ipython',
        'advent-of-code-data',  # aocd package
    ],
    author="Abhinav Verma",
    author_email="verma.abhinav275l@gmail.com",
    description="A template generator for Advent of Code solutions in Google Colab",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/averma12/advent_of_code-colab-template",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
