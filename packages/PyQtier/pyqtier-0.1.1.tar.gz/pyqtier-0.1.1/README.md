# PyQtier (BETA)

Make your onw desktop app faster

## Quick start

### Installing

1. Creating virtual environment

```bash
virtualenv -p python3 .venv
```

2. Activating venv

**Linux / MacOS**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.\.venv\Scripts\activate
```

3. Installing last version of module

```bash
pip install pyqtier
```

_If you want, you can install last test version from Test PyPI_

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyqtier
```

### Creating project

For creating project you need to run follow command: 
```bash
pyqtier startproject <project_path_and_name>
```

where `<project_path_and_name>` can be just `.` if you want to create project in current folder.

### Run project

```bash 
python main.py
```

## Detailed docs

1. [Plugins](docs/PLUGINS.md)


