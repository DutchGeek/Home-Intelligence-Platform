#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bash "${SCRIPT_DIR}/tools/deploy-prod.sh" "$@"
exit $?
