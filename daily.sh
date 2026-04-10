#!/bin/bash
# daily.sh
# Runs one full day of banking: multiple front end sessions, merges the
# transaction files, then runs the back end.
#
# Usage:
#   ./daily.sh <current_accounts> <master_accounts> <new_current_accounts> <new_master_accounts> <session1> [session2 ...]

set -e

if [ "$#" -lt 5 ]; then
    echo "Usage: $0 <current_accounts> <master_accounts> <new_current_accounts> <new_master_accounts> <session1> [session2 ...]"
    exit 1
fi

CURRENT_ACCOUNTS="$1"
MASTER_ACCOUNTS="$2"
NEW_CURRENT_ACCOUNTS="$3"
NEW_MASTER_ACCOUNTS="$4"
shift 4
SESSIONS=("$@")

# Find the directory this script is in so we can call main.py and backend_main.py
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Temp folder to hold the per-session transaction files
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

MERGED_TXN="$WORK_DIR/merged_transactions.atf"

# Step 1: run the front end once per session input file
echo "Running front end sessions..."
SESSION_NUM=0
TXN_FILES=()

for SESSION_INPUT in "${SESSIONS[@]}"; do
    SESSION_NUM=$((SESSION_NUM + 1))
    TXN_OUT="$WORK_DIR/session_${SESSION_NUM}.atf"

    echo "  Session $SESSION_NUM: $SESSION_INPUT"
    python3 "$SCRIPT_DIR/main.py" "$CURRENT_ACCOUNTS" "$TXN_OUT" < "$SESSION_INPUT"

    TXN_FILES+=("$TXN_OUT")
done

# Step 2: merge all session transaction files into one
echo "Merging $SESSION_NUM transaction file(s)..."
cat "${TXN_FILES[@]}" > "$MERGED_TXN"

# Step 3: run the back end on the merged file
echo "Running back end..."
python3 "$SCRIPT_DIR/backend_main.py" \
    "$MASTER_ACCOUNTS" \
    "$MERGED_TXN" \
    "$NEW_MASTER_ACCOUNTS" \
    "$NEW_CURRENT_ACCOUNTS"

echo "Done. New current accounts: $NEW_CURRENT_ACCOUNTS"
echo "Done. New master accounts:  $NEW_MASTER_ACCOUNTS"
