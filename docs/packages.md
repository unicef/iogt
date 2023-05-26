## For Virtual Environment

### Add/Update package:
- Add or update the package and its version specifier according to your needs in <requirements_file>.in file.

Next, run the following commands to generate the compiled <requirements_file>.txt file:
```
pip install --upgrade pip
pip install pip-tools
pip-compile --generate-hashes --resolver=backtracking -o <requirements_file>.txt <requirements_file>.in
```

## For Docker

### Add/Update package:
- Add or update the package and its version specifier according to your needs in <requirements_file>.in file.

Next, run the following command to generate the compiled <requirements_file>.txt file:
```
make cr
```