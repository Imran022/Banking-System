#!/bin/bash
# check_tests.sh
# Validates test outputs by comparing actual results against expected results.
# Must be run after run_tests.sh.
#
# For each test, two comparisons are made:
#   1. Terminal output (.out) vs expected terminal output (.eout)
#   2. Transaction file (.atf) vs expected transaction file (.etf)
#
# Usage: ./check_tests.sh
# Requires: Python 3, sample_accounts.txt in the same directory
# NOTE: --strip-trailing-cr handles Windows/Linux line ending differences

pass=0
fail=0

for i in inputs/TC-*; do
    testname=$(basename $i)

    # Check terminal output against expected
    if diff --strip-trailing-cr -q outputs/$testname.out expected/$testname.eout > /dev/null 2>&1; then
        echo "PASS [$testname] terminal output"
        ((pass++))
    else
        echo "FAIL [$testname] terminal output"
        diff --strip-trailing-cr outputs/$testname.out expected/$testname.eout
        echo ""
        ((fail++))
    fi

    # Check transaction file against expected
    if diff --strip-trailing-cr -q outputs/$testname.atf expected/$testname.etf > /dev/null 2>&1; then
        echo "PASS [$testname] transaction file"
        ((pass++))
    else
        echo "FAIL [$testname] transaction file"
        diff --strip-trailing-cr outputs/$testname.atf expected/$testname.etf
        echo ""
        ((fail++))
    fi
done

echo "================================"
echo "Results: $pass passed, $fail failed"
