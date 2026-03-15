# Phase 3 Failure Log

Use one row per observed failure during testing. Update the row after you fix the issue and rerun tests.

| Test Name | What Was Being Tested | Nature of Failure | Error in Code/Test | Action Taken to Fix It | Status |
|---|---|---|---|---|---|
| `ALL_TESTS` | Phase 3 command-line automation setup | Program could not be run with current-accounts and transaction-output file names as CLI arguments | `main.py` only supported prompted account-file input and auto-generated transaction filename | Added Phase 3 CLI mode: `python main.py <current_accounts_file> <transaction_output_file>` | Fixed |
| `TC-10` | Duplicate account creation prevention in admin mode | Second `create` in the same session was accepted with the same generated account number | Duplicate check only looked at loaded accounts, not pending `CREATE` transactions in the current session | Added duplicate check against pending `CREATE` transactions before accepting create | Fixed |
| `TC-14` | Multi-session test run output isolation | Transaction file written on later logout included earlier session transactions from the same program run | Session transaction list was not cleared after writing the transaction file | Cleared `self.system.transactions` after successful transaction-file write | Fixed |
| `ALL_TESTS` | Portable terminal-output diffing across environments | Logs contained absolute transaction output paths, making expected logs machine-path-specific | `scripts/run_tests.sh` passed absolute output paths to `main.py`, and the program prints the path it writes | Updated `scripts/run_tests.sh` to pass a stable repo-relative transaction output path for default runs | Fixed |

## Notes
- Include failures caused by incorrect tests as well as code defects.
- After fixes, rerun all tests and confirm no regressions.
