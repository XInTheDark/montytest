#!/bin/sh
set -eu

secret_path="${MONTYTEST_SECRET_PATH:-$HOME/montytest.secret}"

if [ -n "${MONTYTEST_SECRET_FILE:-}" ]; then
    if [ ! -s "$MONTYTEST_SECRET_FILE" ]; then
        echo "MONTYTEST_SECRET_FILE is set but the file is missing or empty: $MONTYTEST_SECRET_FILE" >&2
        exit 1
    fi
    mkdir -p "$(dirname "$secret_path")"
    cp "$MONTYTEST_SECRET_FILE" "$secret_path"
    chmod 600 "$secret_path"
elif [ -n "${MONTYTEST_SECRET:-}" ]; then
    mkdir -p "$(dirname "$secret_path")"
    printf '%s' "$MONTYTEST_SECRET" > "$secret_path"
    chmod 600 "$secret_path"
fi

if [ ! -s "$secret_path" ]; then
    echo "Missing montytest auth secret. Set MONTYTEST_SECRET or mount a file and point MONTYTEST_SECRET_FILE at it." >&2
    exit 1
fi

exec "$@"
