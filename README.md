# Flask Schema

This is an experiment to validate input and output data in a Flask application using [Pydantic](https://docs.pydantic.dev/latest/).
It's very much inspired by the [quart-schema](https://quart-schema.readthedocs.io/en/latest/tutorials/quickstart.html)
project.

It is not a **library**, just a pet project where I take ideas from quart-schemas to use them in a flask project.

## Installation

You will need **Python 3.11** or higher to run the project and poetry to install it.

```shell
$ poetry install
```

## Run the application

To run the development server:

```shell
$ flask --app flask_schema.main run --debug
```

To see the available routes:

```shell
$ flask --app flask_schema.main routes
```