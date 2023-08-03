# Introduce pip-tools

## What is it?
Pip-tools is a command-line toolset for managing dependencies in Python projects. It streamlines the process of handling project dependencies by providing essential functionalities.

## Why do we use it?

### Dependency Management

Pip-tools helps manage a project's dependencies by resolving and pinning specific versions. It ensures that everyone working on the project uses the same versions of dependencies, promoting consistency and reproducibility.

### Simplified Workflow

The requirements.in file contains high-level dependencies, while the requirements.txt file contains the pinned versions. This separation enables easy updating and maintenance of dependencies.

## How do we use it?

### For virtual environment:

Install or upgrade pip.

```sh
pip install --upgrade pip
```

Install pip-tools.

```sh
pip install pip-tools
```

To generate pinned versions, add or update a package and its version specifier according to your needs in the _requirements.in_ or _requirements.dev.in_ file.

```sh
pip-compile --generate-hashes --resolver=backtracking -o <requirements_file>.txt <requirements_file>.in
```

### For Docker

Add or update the package and its version specifier according to your needs in a _\*.in_ file. In the project root directory.

```
make compile-requirements
```

Alternatively, you could run `pip-compile` directly on the dev container.

```
docker compose run --rm django pip-compile ...
```
