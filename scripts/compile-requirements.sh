#!/bin/bash

REQ_FILES=(
  "/app/requirements"
  "/app/requirements.dev"
)

for f in "${REQ_FILES[@]}"; do
  pip-compile --cache-dir=/tmp/pip-tools \
              --generate-hashes \
              --resolver=backtracking \
              --output-file ${f}.txt \
              ${f}.in \
      || exit 1;
done
