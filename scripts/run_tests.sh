#!/usr/bin/env sh
#
# Phase 3 test runner for the Front End.
# Runs all transaction input files and saves both terminal output and transaction files.

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
INPUT_DIR="${1:-$ROOT_DIR/tests/inputs}"
ACCOUNTS_FILE="${2:-$ROOT_DIR/sample_accounts.txt}"
OUTPUT_DIR="${3:-$ROOT_DIR/tests/outputs}"

LOG_DIR="$OUTPUT_DIR/logs"
TX_DIR="$OUTPUT_DIR/transactions"

mkdir -p "$LOG_DIR" "$TX_DIR"
cd "$ROOT_DIR"

found_any=0
for input_file in "$INPUT_DIR"/*.in; do
    if [ ! -e "$input_file" ]; then
        continue
    fi
    found_any=1
    test_name="$(basename "$input_file" .in)"
    if [ "$OUTPUT_DIR" = "$ROOT_DIR/tests/outputs" ]; then
        rel_tx_out="tests/outputs/transactions/$test_name.atf"
        log_out="$ROOT_DIR/tests/outputs/logs/$test_name.out"
    else
        rel_tx_out="$TX_DIR/$test_name.atf"
        log_out="$LOG_DIR/$test_name.out"
    fi
    echo "running test $test_name"
    "$PYTHON_BIN" "$ROOT_DIR/main.py" "$ACCOUNTS_FILE" "$rel_tx_out" < "$input_file" > "$log_out"
done

if [ "$found_any" -eq 0 ]; then
    echo "No test input files found in $INPUT_DIR (*.in)." >&2
    exit 1
fi
