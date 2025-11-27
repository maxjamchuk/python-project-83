#!/usr/bin/env bash

set -e

curl -LsSf https://astral.sh/uv/install.sh | sh
# shellcheck disable=SC1090
source "$HOME/.local/bin/env"

make install
psql -a -d "$DATABASE_URL" -f database.sql
