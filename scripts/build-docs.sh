#!/bin/sh

set -e -x
cd "$(dirname "${0}")/.."

python -m mkdocs build

cp ./docs/index.md ./README.md
