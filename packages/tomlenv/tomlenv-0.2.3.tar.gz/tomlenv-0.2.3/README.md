# TOMLenv
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/joaonsantos/tomlenv/python-publish.yml)
![PyPI - Version](https://img.shields.io/pypi/v/tomlenv)
![Pypi - Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tomlenv)
![License](https://img.shields.io/github/license/joaonsantos/tomlenv)

Environment wrapped TOML. 

Package available in [PyPI](https://pypi.org/project/tomlenv/).

## Getting Started

### Install the library

Using pip:
```sh
$ pip install tomlenv
```

Using pipenv:
```sh
$ pipenv install tomlenv
```

Using poetry:
```sh
$ poetry add tomlenv
```

### Basic Usage

Tomlenv takes advantage of modern Python features such as `dataclasses` and
`tomllib` to create a simple yet powerful configuration library.

By default, tomlenv looks for a `config.toml` file in your project root:
```toml
token = "dev"
debug = false
```

Assuming this environment variable is set:
```sh
TOMLENV_DEBUG=true
```

Create your configuration dataclass and parse config and env into it:
```python
import tomlenv
from dataclasses import dataclass

@dataclass
class Config:
    token: str = ''
    debug: bool = False

config = Config()
parser = tomlenv.Parser()

parser.load(config)

# You can now access the fields of your fully typed config Class
# that contains values from a TOML config file and the environment.

# For example:

token = config.token
debug = config.debug
print(token) # prints "dev"
print(debug) # prints True
```

## Configuration

To configure the location of your toml file, set `TOMLENV_CONF_FILEPATH`.

For example if your config file is in `configs/config.toml` relative to the project root, then set `TOMLENV_CONF_FILEPATH=configs/config.toml`

## Tests

This project uses [Poetry](https://python-poetry.org/) and [GNU Make](https://www.gnu.org/software/make/).

Run tests from the project root with:
```sh
$ make test
```

To get a coverage report:
```sh
$ make cov
```

## Issues

Feel free to send issues or suggestions to https://github.com/joaonsantos/tomlenv/issues.
