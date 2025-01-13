[![codecov](https://codecov.io/gh/Strovsk/EscribaLogger/graph/badge.svg?token=FJFYOM8X4U)](https://codecov.io/gh/Strovsk/EscribaLogger)

<p align="center">
   <img src="https://raw.githubusercontent.com/Strovsk/EscribaLogger/refs/heads/main/docs/assets/escriba%20logger%20background.png" alt="Escriba Logger Logo" width="300">
</p>

# Get Started

## install

`python -m pip install EscribaLogger`

## Usage

Just import, add drivers and use:

> You can output your logs using a pre-configured builtin [rich](https://rich.readthedocs.io/en/stable/introduction.html) stdout handler

```python
from EscribaLogger import Log

# Initilize
Log()
Log.set_logger_name('CustomName')

# Add drivers (stdout, file, graylog, flutend etc)
Log.add_driver('stdout')

Log.info('My info message', {'context_var': 'value'})
# > [01/12/25 20:30:20] INFO     CustomName - My info message                                                                <stdin>:1
```

## Log file driver

```python
# You can add another driver. In this case, we will add the file driver
Log.add_driver('file')


Log.info('Some message', extra={"context_var": "value"})
# > The message will be stored in "logs/2023-07-16.log"
# > [2023-07-16 16:13:55,100] EscribaLogger.INFO - Some message - {"context_var": "value"}
```

> In the default logging system, handle context variables is a exhausting task. EscribaLogger added the "extra_context" log variable to solve this. You add the context info for any custom driver.

### Change default log files storage

```python
# You can change default path to store log files in:
Log.add_driver('file', driver_option={'file_location': 'another/path'})


Log.info('Some message', extra={"context_var": "value"})
# > The message will be stored in "another/path/2023-07-16.log"
# > [2023-07-16 16:13:55,100] EscribaLogger.INFO - Some message - {"context_var": "value"}
```

# Contributing

## Setup env

1. install pdm

```console
python -m pip install pdm
```

2. install dependencies

```console
pdm install
```

## Tests

We are using [pytest](https://docs.pytest.org/en/7.4.x/) and [coverage.py](https://coverage.readthedocs.io/en/7.2.7/) to maintain this project.
You can run the tests by using:

```console
pdm run test:unit
```

the command above will generate the `.coverage` file in root path. Now you can generate the coverage report

### Coverage

```console
coverage report -m
```

Or you can create a entire webpage to see the results:

```console
pdm run coverage html
```
