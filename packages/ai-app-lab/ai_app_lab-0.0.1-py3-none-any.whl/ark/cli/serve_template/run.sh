#!/bin/bash
set -ex
# shellcheck disable=SC2046
cd `dirname $0`

exec python3 code/main.py