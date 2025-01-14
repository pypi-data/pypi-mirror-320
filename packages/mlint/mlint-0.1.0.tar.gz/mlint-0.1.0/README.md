# mlint 
*ML Model Intercomparison: Enables efficient evaluation of ML weather forecast models for use within the Met Office. It is enabling the comparison of ML models (including FastNet) and physics-based weather forecast models to make appropriate choices for different use cases.*

This library provides building blocks to run an intercomparison project from a workflow or a data pipeline.

## Installing mlint
You might need a python virtual environment to install mlint and its dependencies. You can create one either using conda or python:
### Conda
```bash
conda create -n mlint_env -c conda-forge -y python=3.11
conda activate mlint_env
```
### Python
```bash
python -m venv <path>/mlint_env  
source <path>/mlint_env/bin/activate
```
### Install mlint
```bash
make install
```

This will install mlint in the active virtual environment together with all the dependencies

### Installing the development environment
```bash
make depend  # if dependencies haven't been installed yet, e.g. make install
make dev     # only the first time
make test
```