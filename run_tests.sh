#!/bin/bash
# run_tests.sh
# Runs all test input files through the banking system front end.
# Usage: ./run_tests.sh
# Saves transaction files (.atf) and terminal logs (.out) to outputs/

mkdir -p outputs

for i in inputs/TC-*; do
    testname=$(basename $i)
    echo "Running test $testname..."
    python3 main.py sample_accounts.txt outputs/$testname.atf < $i > outputs/$testname.out 2>&1
done

echo ""
echo "All tests complete. Results in outputs/"
