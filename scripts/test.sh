#!/usr/bin/env bash

set -e
set -x

pytest --cov=bollywood_data_science --cov=tests --cov-report=term-missing ${@}
bash ./scripts/lint.sh
