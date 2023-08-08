#!/bin/bash

WORKDIR=/app
REQ_FILES=(
  "requirements"
  "requirements.dev"
)

cd $WORKDIR

for f in "${REQ_FILES[@]}"; do
  pip-compile --generate-hashes \
              --resolver=backtracking \
              --output-file ${f}.txt \
              ${f}.in \
      || exit 1;
done
