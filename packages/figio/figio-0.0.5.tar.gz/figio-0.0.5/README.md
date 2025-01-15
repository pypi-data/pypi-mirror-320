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

## Distribution

The distribution steps will tag the code state as a release version, with a semantic version number, build the code as a wheel file, and publish to the wheel file as a release to GitHub.

### Tag

View existing tags, if any:

```bash
git tag
```

Create a tag.  Tags can be *lightweight* or *annotated*.
Annotated tags are recommended since they store tagger name, email, date, and
message information.  Create an annotated tag:

```bash
# example of an annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"
```

Push the tag to repo

```bash
# example continued
git push origin v1.0.0
```

Verify the tag appears on the repo

### Build

Ensure that `setuptools` and `build` are installed:

```bash
pip install setuptools build
```

Navigate to the project directory, where the `pyproject.toml` file is located
and create a wheel distribution.

```bash
# generates a .whl file in the dist directory
python -m build --wheel
```
