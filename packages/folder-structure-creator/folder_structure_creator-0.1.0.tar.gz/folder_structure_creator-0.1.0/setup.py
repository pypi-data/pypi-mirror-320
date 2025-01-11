from setuptools import setup, find_packages

setup(
    name="folder_structure_creator",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'fstruct=fstruct.main:main',
        ],
    },
    install_requires=[
        # Add any dependencies here
    ],
    author="NagiEight",
    author_email="nagieight22@gmail.com",
    description="A tool to create folder structures based on text files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NagiEight/folder-structure-creator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
