#!/bin/bash
# weekly.sh
# Simulates seven days of banking by calling daily.sh once per day.
# Each day uses a different set of Front End transaction sessions, and
# each day's new Current/Master files become the next day's inputs.
#
# Usage:
#   ./weekly.sh <initial_current_accounts> <initial_master_accounts>

set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <initial_current_accounts> <initial_master_accounts>"
    exit 1
fi

INITIAL_CURRENT="$1"
INITIAL_MASTER="$2"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAILY_SCRIPT="$SCRIPT_DIR/daily.sh"
INPUTS_DIR="$SCRIPT_DIR/inputs"

WEEKLY_WORK_DIR="$SCRIPT_DIR/weekly_run_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$WEEKLY_WORK_DIR"

echo "Starting 7-day simulation. Output folder: $WEEKLY_WORK_DIR"
echo ""

DAY1_SESSIONS=("$INPUTS_DIR/TC-01" "$INPUTS_DIR/TC-04" "$INPUTS_DIR/TC-07")
DAY2_SESSIONS=("$INPUTS_DIR/TC-02" "$INPUTS_DIR/TC-03" "$INPUTS_DIR/TC-08")
DAY3_SESSIONS=("$INPUTS_DIR/TC-05" "$INPUTS_DIR/TC-06" "$INPUTS_DIR/TC-09")
DAY4_SESSIONS=("$INPUTS_DIR/TC-10" "$INPUTS_DIR/TC-11" "$INPUTS_DIR/TC-12")
DAY5_SESSIONS=("$INPUTS_DIR/TC-13" "$INPUTS_DIR/TC-14" "$INPUTS_DIR/TC-15")
DAY6_SESSIONS=("$INPUTS_DIR/TC-16" "$INPUTS_DIR/TC-17" "$INPUTS_DIR/TC-18")
DAY7_SESSIONS=("$INPUTS_DIR/TC-19" "$INPUTS_DIR/TC-20" "$INPUTS_DIR/TC-21")

CURRENT_ACCOUNTS="$INITIAL_CURRENT"
MASTER_ACCOUNTS="$INITIAL_MASTER"

for DAY in 1 2 3 4 5 6 7; do
    echo "Day $DAY"

    DAY_DIR="$WEEKLY_WORK_DIR/day${DAY}"
    mkdir -p "$DAY_DIR"

    NEW_CURRENT="$DAY_DIR/day${DAY}_current_accounts.txt"
    NEW_MASTER="$DAY_DIR/day${DAY}_master_accounts.txt"

    case $DAY in
        1) SESSIONS=("${DAY1_SESSIONS[@]}") ;;
        2) SESSIONS=("${DAY2_SESSIONS[@]}") ;;
        3) SESSIONS=("${DAY3_SESSIONS[@]}") ;;
        4) SESSIONS=("${DAY4_SESSIONS[@]}") ;;
        5) SESSIONS=("${DAY5_SESSIONS[@]}") ;;
        6) SESSIONS=("${DAY6_SESSIONS[@]}") ;;
        7) SESSIONS=("${DAY7_SESSIONS[@]}") ;;
    esac

    bash "$DAILY_SCRIPT" \
        "$CURRENT_ACCOUNTS" \
        "$MASTER_ACCOUNTS" \
        "$NEW_CURRENT" \
        "$NEW_MASTER" \
        "${SESSIONS[@]}"

    echo ""

    CURRENT_ACCOUNTS="$NEW_CURRENT"
    MASTER_ACCOUNTS="$NEW_MASTER"
done

echo "Weekly simulation complete."
echo "Final current accounts: $CURRENT_ACCOUNTS"
echo "Final master accounts:  $MASTER_ACCOUNTS"
