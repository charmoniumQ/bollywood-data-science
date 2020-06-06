#!/bin/sh

set -e -x
cd "$(dirname "${0}")/.."

poetry publish  --build
