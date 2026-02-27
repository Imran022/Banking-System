#!/bin/bash
# check_tests.sh
# Compares actual outputs against expected outputs (terminal + transaction file).
# Usage: ./check_tests.sh
# Reports PASS or FAIL for each test.

pass=0
fail=0

for i in inputs/TC-*; do
    testname=$(basename $i)

    # Check terminal output
    if diff -q outputs/$testname.out expected/$testname.eout > /dev/null 2>&1; then
        echo "PASS [$testname] terminal output"
        ((pass++))
    else
        echo "FAIL [$testname] terminal output"
        diff outputs/$testname.out expected/$testname.eout
        echo ""
        ((fail++))
    fi

    # Check transaction file
    if diff -q outputs/$testname.atf expected/$testname.etf > /dev/null 2>&1; then
        echo "PASS [$testname] transaction file"
        ((pass++))
    else
        echo "FAIL [$testname] transaction file"
        diff outputs/$testname.atf expected/$testname.etf
        echo ""
        ((fail++))
    fi
done

echo "================================"
echo "Results: $pass passed, $fail failed"
