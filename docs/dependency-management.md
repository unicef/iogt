# Introduce pip-tools

## What is it?
Pip-tools is a command-line toolset for managing dependencies in Python projects. 
It streamlines the process of handling project dependencies by providing essential functionalities.

## Why do we use it?

### Dependency Management
Pip-tools helps manage a project's dependencies by resolving and pinning specific versions. 
It ensures that everyone working on the project uses the same versions of dependencies, promoting consistency and reproducibility.

### Simplified Workflow
Pip-tools simplifies the workflow of managing dependencies by keeping the requirements.in file separate from the requirements.txt file. 
The requirements.in file contains high-level dependencies, while the requirements.txt file contains the pinned versions. This separation enables easy updating and maintenance of dependencies.

## How do we use it?

### For Virtual Environment:

#### Install or Upgrade pip:
```pip install --upgrade pip```

#### Install pip-tools:
```pip install pip-tools```

#### Generate Pinned Versions:
Add or update the package and its version specifier according to your needs in <requirements_file>.in file.

```pip-compile --generate-hashes --resolver=backtracking -o <requirements_file>.txt <requirements_file>.in```

### For Docker
Add or update the package and its version specifier according to your needs in <requirements_file>.in file.

```
make compile-requirements
```