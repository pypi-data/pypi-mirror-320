# emi-re

[![PyPI - Version](https://img.shields.io/pypi/v/emi-re.svg)](https://pypi.org/project/emi-re)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/emi-re.svg)](https://pypi.org/project/emi-re)

Emi-re (pronunciation: [Emily](https://millionlive-theaterdays.idolmaster-official.jp/idol/emily/)) is a collection of regular expressions encountered during OSS code reading.

-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install emi-re
```

## Usage

CamelCase to snake_case

```python
>>> import emire
>>> emire.to_snake_case("CamelCase")
'camel_case'

```

Remove whitespaces (in Japanese)

```python
>>> import emire
>>> emire.remove_spaces("Algorithm C ないしは アルゴリズム C")
'Algorithm CないしはアルゴリズムC'

```

## License

`emi-re` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
