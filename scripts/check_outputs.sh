#!/usr/bin/env sh
#
# Phase 3 output validator for the Front End.
# Compares actual terminal and transaction outputs to expected files using diff.

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
INPUT_DIR="${1:-$ROOT_DIR/tests/inputs}"
EXPECTED_DIR="${2:-$ROOT_DIR/tests/expected}"
OUTPUT_DIR="${3:-$ROOT_DIR/tests/outputs}"

EXPECTED_LOG_DIR="$EXPECTED_DIR/logs"
EXPECTED_TX_DIR="$EXPECTED_DIR/transactions"
ACTUAL_LOG_DIR="$OUTPUT_DIR/logs"
ACTUAL_TX_DIR="$OUTPUT_DIR/transactions"

status=0
found_any=0

for input_file in "$INPUT_DIR"/*.in; do
    if [ ! -e "$input_file" ]; then
        continue
    fi
    found_any=1
    test_name="$(basename "$input_file" .in)"
    echo "checking outputs for $test_name"

    expected_log="$EXPECTED_LOG_DIR/$test_name.out"
    actual_log="$ACTUAL_LOG_DIR/$test_name.out"
    expected_tx="$EXPECTED_TX_DIR/$test_name.atf"
    actual_tx="$ACTUAL_TX_DIR/$test_name.atf"

    if [ ! -f "$expected_log" ]; then
        echo "Missing expected terminal output: $expected_log" >&2
        status=1
    elif [ ! -f "$actual_log" ]; then
        echo "Missing actual terminal output: $actual_log" >&2
        status=1
    else
        diff -u "$expected_log" "$actual_log" || status=1
    fi

    if [ ! -f "$expected_tx" ]; then
        echo "Missing expected transaction file: $expected_tx" >&2
        status=1
    elif [ ! -f "$actual_tx" ]; then
        echo "Missing actual transaction file: $actual_tx" >&2
        status=1
    else
        diff -u "$expected_tx" "$actual_tx" || status=1
    fi
done

if [ "$found_any" -eq 0 ]; then
    echo "No test input files found in $INPUT_DIR (*.in)." >&2
    exit 1
fi

exit "$status"
