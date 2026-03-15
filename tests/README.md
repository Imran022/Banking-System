# Phase 3 Test Layout

Place your Phase 1 acceptance tests and expected outputs in this structure:

- `tests/inputs/*.in` : transaction input streams (stdin for each test)
- `tests/expected/logs/*.out` : expected terminal output for each test
- `tests/expected/transactions/*.atf` : expected transaction file for each test
- `tests/outputs/` : actual outputs produced by scripts (auto-generated)

Naming rule:
- Base names must match across all three files.
- Example:
  - `tests/inputs/test_login_withdraw.in`
  - `tests/expected/logs/test_login_withdraw.out`
  - `tests/expected/transactions/test_login_withdraw.atf`

Run all tests:

```sh
sh scripts/run_tests.sh
sh scripts/check_outputs.sh
```

On Windows, run these Unix shell scripts from Git Bash or WSL.

Optional arguments:

```sh
sh scripts/run_tests.sh <input_dir> <current_accounts_file> <output_dir>
sh scripts/check_outputs.sh <input_dir> <expected_dir> <output_dir>
```
