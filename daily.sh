#!/bin/bash
# daily.sh
# Runs one full day of banking by:
#   1. running the Front End once per supplied transaction session,
#   2. saving each session transaction file,
#   3. concatenating them into one merged daily transaction file, and
#   4. running the Back End on the merged file.
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

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$(cd "$(dirname "$NEW_CURRENT_ACCOUNTS")" && pwd)"
CURRENT_NAME="$(basename "$NEW_CURRENT_ACCOUNTS")"
DAY_PREFIX="${CURRENT_NAME%_current_accounts.txt}"
if [ "$DAY_PREFIX" = "$CURRENT_NAME" ]; then
    DAY_PREFIX="daily_run"
fi
ARTIFACT_DIR="$OUTPUT_DIR/${DAY_PREFIX}_artifacts"
mkdir -p "$ARTIFACT_DIR"

MERGED_TXN="$ARTIFACT_DIR/merged_transactions.atf"

echo "Running front end sessions..."
SESSION_NUM=0
TXN_FILES=()

for SESSION_INPUT in "${SESSIONS[@]}"; do
    SESSION_NUM=$((SESSION_NUM + 1))
    TXN_OUT="$ARTIFACT_DIR/session_${SESSION_NUM}.atf"

    echo "  Session $SESSION_NUM: $SESSION_INPUT"
    python3 "$SCRIPT_DIR/main.py" "$CURRENT_ACCOUNTS" "$TXN_OUT" < "$SESSION_INPUT"

    TXN_FILES+=("$TXN_OUT")
done

echo "Merging $SESSION_NUM transaction file(s)..."
cat "${TXN_FILES[@]}" > "$MERGED_TXN"

echo "Running back end..."
python3 "$SCRIPT_DIR/backend_main.py" \
    "$MASTER_ACCOUNTS" \
    "$MERGED_TXN" \
    "$NEW_MASTER_ACCOUNTS" \
    "$NEW_CURRENT_ACCOUNTS"

echo "Done. New current accounts: $NEW_CURRENT_ACCOUNTS"
echo "Done. New master accounts:  $NEW_MASTER_ACCOUNTS"
echo "Saved session transaction files in: $ARTIFACT_DIR"
echo "Saved merged daily transaction file: $MERGED_TXN"
