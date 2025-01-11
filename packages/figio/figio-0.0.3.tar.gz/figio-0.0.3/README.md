# figio

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