#!/usr/bin/env bash

set -e
set -x

mypy bollywood_data_science --disallow-untyped-defs
black bollywood_data_science tests --check
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --check-only --thirdparty bollywood_data_science bollywood_data_science tests
