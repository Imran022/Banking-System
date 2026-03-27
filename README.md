# Banking System - Phases 3 to 5

This repository contains the console-based CSCI 3060U Banking System implementation for:

- the Front End ATM session flow from Phases 2-3
- the new Phase 4 Back End overnight batch processor
- the Phase 5 white-box unit tests and test report for the Back End

## Front End Run

```bash
python main.py <current_accounts_file> <transaction_output_file>
```

Example:

```bash
python main.py sample_accounts.txt transout.atf
```

## Back End Run

```bash
python backend_main.py <old_master_file> <merged_transaction_file> <new_master_file> <new_current_file>
```

## Files and Formats

- Current accounts input supports the original layout and the optional plan-aware variant (`SP`/`NP`) to match the course discrepancy note.
- Master accounts input supports the original Phase 4 layout and can also read the plan-aware starter-code style when present.
- The Back End preserves the plan-field style it receives in the old master file instead of always forcing the extended format.

## Main Source Files

- `main.py`: Front End CLI and guided transaction prompts
- `banking_system.py`: Front End session orchestration
- `validator.py`: Front End business-rule validation
- `backend_main.py`: Back End CLI entry point
- `batch_processor.py`: Back End transaction application and constraint logging
- `file_handler.py`: shared fixed-width file parsing and writing
- `account.py`: shared account model for current and master files
- `transaction.py`: shared transaction model and file serialization

## Tests

- Front End regression scripts: `bash scripts/run_tests.sh` then `bash scripts/check_outputs.sh`
- Back End/unit tests: `python -m unittest discover -s tests -p "test_*.py"`
- Phase 5 white-box tests: `C:\Users\waizm\AppData\Local\Python\pythoncore-3.14-64\python.exe -m unittest tests.test_phase5_whitebox -v`

## Design Deliverable

- `PHASE4_DESIGN.md`: Phase 4 architecture, UML-style class overview, and class/method intention table
- `PHASE5_TEST_REPORT.md`: Phase 5 Back End white-box coverage analysis and test results
