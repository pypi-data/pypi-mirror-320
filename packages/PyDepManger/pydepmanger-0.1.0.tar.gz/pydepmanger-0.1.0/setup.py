import setuptools
from pathlib import Path

def parse_requirements(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

setuptools.setup(
    name="PyDepManger",
    
    author="Example Author1, Another Author2",
    author_email="author2@example.com, another2@example.com",
    
    maintainer="John, Jane",
    maintainer_email="john@example.com, jane@example.com",
    python_requires=">=3.10",

    
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    
    url="https://github.com/abuawadd/PyDepManger",
    
    project_urls={
        "Documentation": "https://github.com/abuawadd/PyDepManger/wiki",
        "Source": "https://github.com/abuawadd/PyDepManger",
        "Changelog": "https://github.com/abuawadd/PyDepManger/blob/main/CHANGELOG.md",
    },

    
    keywords=["example", "demo", "setuptools", "package"], #


    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: C",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],

    install_requires=parse_requirements('requirements.txt'),
    packages=setuptools.find_packages(),
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
