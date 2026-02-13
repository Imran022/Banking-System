# Banking System Front End - Phase 2

This repository contains a Phase 2 rapid prototype of the CSCI 3060U Banking System Front End.
The implementation is console-based, intentionally simple, and organized for readability.

## Rubric Alignment (Phase 2)

- Console application (terminal I/O only)
- Reads the Current Bank Accounts file during login
- Processes required Front End transaction codes
- Writes Bank Account Transaction file on logout
- Includes class/method documentation and design document

## Run

```bash
python main.py
```

## Input and Output

Input file:
- Current Bank Accounts File (fixed-width, 37 chars per account line), prompted during login

Output file:
- Bank Account Transaction File written on logout as `transaction_file_YYYY-MM-DD.txt`

Console I/O:
- Reads commands and prompted values from stdin
- Prints prompts/results/errors to stdout

## Commands

- `login`
- `logout`
- `withdrawal` (`withdraw` alias)
- `transfer`
- `paybill`
- `deposit`
- `create`
- `delete`
- `disable`
- `changeplan`

## Source Files

- `main.py`: console interaction and transaction prompt flow
- `banking_system.py`: transaction orchestration and session state
- `validator.py`: business-rule validation
- `file_handler.py`: fixed-format file parsing and writing
- `account.py`: account entity
- `transaction.py`: transaction entity and output-line formatting

## Design Deliverable

- `PHASE2_DESIGN.md`: architecture, UML class diagram, and class/method intention table
