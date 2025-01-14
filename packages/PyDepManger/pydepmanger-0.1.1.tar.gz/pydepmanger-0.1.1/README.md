<picture>
        <source srcset="https://github.com/AbuAwadM/PyDepManger/blob/main/Picture10.png?raw=true" media="(prefers-color-scheme: dark)">
        <img src="https://github.com/AbuAwadM/PyDepManger/blob/main/Picture1.png?raw=true" alt="Mode Image">
</picture>

---
<!-- # PyHLicorn -->
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/PyDepManger)
![PyPI - Version](https://img.shields.io/pypi/v/PyDepManger)
![GitHub repo size](https://img.shields.io/github/repo-size/AbuAwadM/PyDepManger)


A Python package that re-implements an existing deprecated R package.

- **[Documentation](https://www.google.co.uk/)**
- **[Source Code](https://www.google.co.uk/)**
- **[Research Paper](https://www.google.co.uk/)**
- **[Issues](https://www.google.co.uk/)**

The PyHLicorn package aims to infer a large-scale transcription co-regulatory network from transcriptomic data and integrate external data on gene regulation to infer and analyze transcriptional programs. The unique aspect of the network inference algorithm proposed in the package is its ability to learn co-regulation networks where gene regulation is modeled by transcription factors acting cooperatively to synergistically regulate target genes.

## About the Project
The package was utilized in a study of Bladder Cancer to identify the driver transcriptional programs from a set of 183 samples. Throughout this vignette, a smaller version of the transcriptomic dataset is used to illustrate the package's usage.

## Installation

To install the package, use pip:
```sh
pip install PyHLicorn
```

To clone the repository, use GitHub:
```sh
git clone https://www.google.co.uk/
```

## Usage
Refer to the [documentation](https://www.google.co.uk/) for detailed usage instructions.

Here is an example of how to use the PyHLicorn package in your Python code:

### Import the Library
```python
import pandas as pd
from PyHLicorn import HLicorn
```

### Import the Data
```python
numerical_expression = pd.read_csv(file_path, index_col=0)
discrete_expression = pd.read_csv(file_path, index_col=0)
tf_list = pd.read_csv(file_path, index_col=0)
```

### Create the Gene Regulatory Network
```python
GRN = HLicorn(numerical_expression, tf_list, discrete_expression)
```
## Authors

- **John Doe** - *Initial work* - [JohnDoe]()
- **Jane Smith** - *Contributor* - [JaneSmith]()

## Maintainers

- **Alice Johnson** - [AliceJohnson]()
- **Bob Brown** - [BobBrown]()

## Credits

- Special thanks to the [XYZ Lab](https://www.xyzlab.com) for their support and resources.
- Thanks to all contributors who have helped improve this project.

## Citation

If you use this package in your research, please cite the following paper:

```
@article{Doe2023,
                                title={PyHLicorn: A Python package for transcription co-regulatory network inference},
                                author={Doe, John and Smith, Jane},
                                journal={Journal of Computational Biology},
                                volume={30},
                                number={4},
                                pages={123-134},
                                year={2023},
                                publisher={Bioinformatics Press}
}
```
