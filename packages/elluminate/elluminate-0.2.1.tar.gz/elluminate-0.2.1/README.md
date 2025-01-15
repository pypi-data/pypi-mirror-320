# Elluminate SDK

**SDK is still WIP and currently not fully working with the SDK, also Docs not yet updated!**

Elluminate SDK is a Software Development Kit that provides a convenient way to interact with the Elluminate platform programmatically. It allows developers to integrate Elluminate functionality into their own applications or scripts, serving as a bridge between custom code and the Elluminate Service API.

## Installation

You can install the Elluminate SDK from GitHub as follows:

```sh
pip install git+ssh://git@github.com/ellamind/elluminate-platform-django.git#subdirectory=elluminate_sdk
```

## Quick Start

### Staging

With the API key set in `ELLUMINATE_API_KEY`:

```python
from elluminate import Client
client = Client()
```

Or with the API key passed directly:

```python
from elluminate import Client
client = Client(api_key=<api-key-here>)
```

### Locally

The API key handling is the same as in staging, the `Client` must simply be instantiated with a `base_url`

```python
from elluminate import Client
client = Client(base_url="http://localhost:8000")
```

## Development

To set up the development environment:

1. Go to the `elluminate_sdk` directory if not already. This is the directory that this README is in. All commands of this README should be run on this directory level.

``` sh
cd elluminate_sdk
```

2. Install the SDK with development dependencies:

```bash
uv sync --dev
```

This should create a `.venv` in the `elluminate_sdk` directory. This is a separate environment from the Platforms virtual environment.

## Usage

The Elluminate SDK provides a simple interface for interacting with the Elluminate platform. Import the `Client` class, create a client instance, and use its methods to manage experiments, generate questions, and rate answers.

### Example Usage

The `examples` directory includes a number of scripts showing how to use the SDK.

Note: The examples are configured to run against a service hosted by the default `base_url` defined in the `Client` class. You must set the `ELLUMINATE_BASE_URL` environment variable to override `base_url`.

Example for local:

``` sh
export ELLUMINATE_BASE_URL=http://localhost:8000
```

Example for staging:

``` sh
export ELLUMINATE_BASE_URL=https://dev.elluminate.de
```

Example for production:

``` sh
export ELLUMINATE_BASE_URL=https://elluminate.de
```

### Cookbooks

To run the cookbooks located in the `examples/cookbooks` directory, some extra dependencies are required:

1. Install cookbook dependencies

``` sh
uv sync --extra cookbooks
```

2. Run your chosen cookbook

```sh
uv run python -m examples.cookbooks.<cookbook_name>
```

### Advanced Usage

For basic usage, refer to the `example_sdk_usage_with_collections.py` file in the `examples` directory.

## Development

To set up the development environment:

1. Install the SDK with development dependencies:

```sh
uv sync --dev
```

2. Activate the `uv` virtual environment:

``` sh
source .venv/bin/activate
```

3. To deactivate the virtual environment:

``` sh
deactivate
```

## Running Tests

To run tests for the Elluminate SDK:

1. Install the SDK with development dependencies:

```sh
uv sync --dev
```

2. Run the tests:

```sh
uv run pytest ./elluminate
```

To see test coverage:

```sh
uv run pytest --cov=elluminate --cov-report=term-missing
```

## Publishing

The SDK can be published to PyPI using the following process:

1. Update the version in `__init__.py` following semantic versioning (X.Y.Z)

2. Push your changes to GitHub.

3. Manually run the "Publish SDK to PyPI" GitHub Action using the "Run workflow" button. Type in the version into the field exactly as in Step 1.
   - This action checks that the version you input is indeed the version to be published as defined in the `__init__.py` file. This acts as a santiy check.
   - Builds and publishes the SDK to PyPI
