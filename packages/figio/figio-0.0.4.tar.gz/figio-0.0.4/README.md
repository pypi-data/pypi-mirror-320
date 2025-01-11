# figio

[![pypi](https://img.shields.io/pypi/v/figio?logo=pypi&logoColor=FBE072&label=PyPI&color=4B8BBE)](https://pypi.org/project/figio)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.14630355-blue)](https://doi.org/10.5281/zenodo.14630355)

A declarative method for plotting (x, y) and histogram data

## Client Configuration

```sh
pip install figio
```

## Developer Configuration

From the `~/autotwin/figio` folder, create the virtual enivronment,

```sh
python -m venv .venv
source .venv/bin/activate       # bash
source .venv/bin/activate.fish  # fish shell
```

Install the code in editable form,

```sh
pip install -e .[dev]
```

## Manual Distribution

```sh
python -m build . --sdist  # source distribution
python -m build . --wheel
twine check dist/*
```
