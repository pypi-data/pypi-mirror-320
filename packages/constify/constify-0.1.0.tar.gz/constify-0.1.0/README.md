[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-%233776AB?style=flat&logo=python&logoColor=%23FFD43B)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-%234FC08D?style=flat)](https://choosealicense.com/licenses/mit/)
[![Coverage Status](https://coveralls.io/repos/github/yazernin10x/constify/badge.svg?branch=main)](https://coveralls.io/github/yazernin10x/constify?branch=main)
[![Unit Tests](https://github.com/yazernin10x/constify/actions/workflows/test.yml/badge.svg)](https://github.com/yazernin10x/constify/actions/workflows/test.yml)
[![Tox](https://img.shields.io/badge/Tox-Passing-%238ACA3E?style=flat)](https://tox.wiki/en/latest/config.html)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/MyPy-Checked-%232A6ACB)](https://mypy-lang.org/)

# Constify

The `constify` library provides the `freezeparams` decorator to make mutable default values and arguments passed to functions immutable.

## Why use the `freezeparams` decorator ?

[[1]](#sources) The default value of a parameter is evaluated only once, which can lead to unexpected behavior if the value is a mutable object, such as a list or a dictionary. For example, the following function accumulates arguments across calls:

### Example
```python
def f(a, L=[]):
    L.append(a)
    return L

print(f(1))  # [1]
print(f(2))  # [1, 2]
print(f(3))  # [1, 2, 3]
```

To prevent this default value from being shared, the function can be rewritten as follows:

```python
def f(a, L=None):
    if L is None:
        L = []
    L.append(a)
    return L
```

This solution is effective, but with multiple mutable default values, it requires many checks. The `freezeparams` decorator simplifies the use of mutable objects as default values and arguments.

## Installation

```bash
pip install constify
```

## Usage

```python
from constify import freezeparams

@freezeparams
def f(a, L=[]):
    L.append(a)
    return L

# Default value (list) remains unchanged
print("f(1) =>", f(1))  # [1]
print("f(2) =>", f(2))  # [2]
print("f(3) =>", f(3))  # [3]

print("-" * 25) # just a separator

# Passed list remains intact
x = [1, 2]
print("x =", x)  # [1, 2]
print(f"f(3, {x}) =>", f(3, x))  # [1, 2, 3]
print(f"f(4, {x}) =>", f(4, x))  # [1, 2, 4]
print("x =", x)  # [1, 2]
```
**You can comment out the decorator and run the code again to see the difference.**

*Simple and effective!*

## Sources

[1] https://docs.python.org/3.13/tutorial/controlflow.html#default-argument-values