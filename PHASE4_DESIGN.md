# Phase 4 Back End Design

## Summary

The Banking System now has two console applications:

- the Front End ATM console, which reads current accounts and writes session transaction files
- the Back End batch processor, which reads the old master accounts file plus a merged transaction file and writes the new master/current account files

The shared model layer keeps the fixed-width file logic in one place so both applications use the same account and transaction structures.

## UML-Style Class Diagram

```text
+-----------------+        +-------------------+        +----------------+
| BankingConsole  | -----> | BankingSystem     | -----> | Validator      |
+-----------------+        +-------------------+        +----------------+
         |                           |
         v                           v
+-----------------+        +-------------------+
| FileHandler     | <----> | Transaction       |
+-----------------+        +-------------------+
         ^
         |
         v
+-----------------+        +-------------------+
| backend_main.py | -----> | BatchProcessor    |
+-----------------+        +-------------------+
         |                           |
         +---------------------------+
                     uses
                       |
                       v
                 +-------------+
                 | Account     |
                 +-------------+
```

## Classes and Methods

| Item | Intention |
|---|---|
| `Account` | Store one bank account, including status, balance, total transactions, and payment plan. |
| `Account.transaction_fee()` | Return the daily per-transaction fee implied by the current payment plan. |
| `Account.to_current_file_string()` | Serialize one account into the next-day Current Bank Accounts format. |
| `Account.to_master_file_string()` | Serialize one account into the Master Bank Accounts format. |
| `Transaction` | Store one bank transaction record shared by the Front End and Back End. |
| `Transaction.to_file_string()` | Serialize a transaction into a merged/session transaction file line. |
| `Transaction.from_file_string()` | Parse one transaction line from a merged batch file. |
| `FileHandler` | Read and write all fixed-width banking files used by both applications. |
| `FileHandler.parse_current_accounts_file()` | Read Current Bank Accounts data with or without the optional plan field. |
| `FileHandler.parse_master_accounts_file()` | Read Master Bank Accounts data with or without the optional plan field. |
| `FileHandler.parse_transaction_file()` | Parse merged bank account transaction records into `Transaction` objects. |
| `FileHandler.generate_current_accounts_file()` | Write sorted next-day current accounts plus the EOF marker. |
| `FileHandler.generate_master_accounts_file()` | Write sorted new master accounts. |
| `FileHandler.generate_transaction_file()` | Write one Front End session's transaction records plus the end-session marker. |
| `BankingSystem` | Manage Front End login state, account access, and accepted transaction requests. |
| `BankingSystem.process_*()` | Validate and stage each supported Front End transaction. |
| `Validator` | Enforce Front End business constraints before a transaction is written to the output file. |
| `BatchProcessor` | Apply merged transaction records to the old master snapshot and log failed constraints. |
| `BatchProcessor.process()` | Run the complete overnight transaction pass in file order. |
| `BatchProcessor.get_accounts()` | Return the final sorted account list for output generation. |
| `backend_main.main()` | Command-line entry point for the Phase 4 Back End. |
| `BankingConsole.run()` | Command-line entry point for the interactive Front End. |

## Data Flow

1. `main.py` loads the current accounts file and accepts Front End transactions.
2. Each successful Front End transaction becomes a `Transaction` record in the session output file.
3. `backend_main.py` reads the old master file and the merged transaction file.
4. `BatchProcessor` applies each non-`00` transaction in sequence.
5. `FileHandler` writes the new master accounts file and the new current accounts file.

## Important Design Decisions

- The Back End is a separate CLI so the ATM interaction flow stays simple.
- The parser is tolerant on input because the course handout and starter code disagree about plan-aware line lengths.
- The writer preserves the master-file style it receives so the output stays closer to the provided input format.
- The current-accounts plan field is treated as optional, matching the discrepancy note shared for the course files.
- Transfer processing uses a compatibility extension so the merged file retains enough information for the Back End to identify the destination account.
