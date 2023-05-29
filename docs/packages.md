- Add or update the package and its version specifier according to your needs in <requirements_file>.in file.

Next, run the following commands to generate the compiled <requirements_file>.txt file:

### For Virtual Environment
```
pip install --upgrade pip
pip install pip-tools
pip-compile --generate-hashes --resolver=backtracking -o <requirements_file>.txt <requirements_file>.in
```

### For Docker
```
make cr
```