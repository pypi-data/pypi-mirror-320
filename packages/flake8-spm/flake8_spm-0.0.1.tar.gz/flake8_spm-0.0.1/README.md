# flake8-spm
Flake8 plugin for finding issues with structural pattern matching

**NOTE**: this plugin is under development. Coming up soon!


## Motivation

Structural pattern matching
has been introduced in [PEP 634](https://peps.python.org/pep-0634/)
with the tutorial added in [PEP 636](https://peps.python.org/pep-0636/).

The present plugin intends to catch default cases,
which do not match any pattern,
but do not raise an exception.

In the problematic example below we handle unexpected pattern as `Default`.

``` python
def func(value):
    match value:
        case 1:
            return 'One'
        case _:
            return 'Default'  # <-- ignoring exceptional case
```

However, for the non-matching cases we would better raise an error,
to follow fail-fast methodology.
Indeed, if we could not find a mathing pattern,
then it is an unexpected event,
and we need to raise an error, as shown below.

``` python
def func(value):
    match value:
        case 1:
            return 'One'
        case _:
            raise ValueError(f'Unexpected case: {value}')
```

Then in the client code we would handle this error appropriately,
instead of sweeping the issue under the rug.


## List of warnings

**SPM001**: not raising when matching default value.


## Installation (IN PROGRESS)

Install via `pip` with:
```
$ pip install flake8-spm
```

It will then automatically be run as part of `flake8`.
You can check is has been picked up via:
```
$ flake8 --version
```
