from setuptools import find_packages, setup


def parse_requirements(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()

requirements = parse_requirements("requirements.txt")


setup(
    name='pytranscripts',
    packages=find_packages(include = ['pytranscripts']),
    version='1.2.4',
    description='A python package for extracting electronic health transcripts ,  and then classifying them based on human annotated data.',
    author='eskayML',
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # long_description=long_description,
    python_requires='>=3.6',
    install_requires=requirements,  # Include the dependencies from requirements.txt
)