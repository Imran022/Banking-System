"""Phase 4 Back End tests for file parsing, transaction formats, and batch processing."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from account import Account
from batch_processor import BatchProcessor
from file_handler import FileHandler
from transaction import Transaction


class FileHandlerPhase4Tests(unittest.TestCase):
    """Verify Phase 4 file parsing across the documented format discrepancies."""

    def test_parse_current_accounts_supports_optional_plan_field(self) -> None:
        handler = FileHandler()
        content = (
            "00001 John Doe             A 01000.00 SP\n"
            "00002 Jane Smith           D 00500.00\n"
            "00000 END_OF_FILE          A 00000.00 NP\n"
        )

        accounts = handler.parse_current_accounts_file(content)

        self.assertEqual(2, len(accounts))
        self.assertEqual(Account.STUDENT_PLAN, accounts[0].get_plan())
        self.assertEqual(Account.NON_STUDENT_PLAN, accounts[1].get_plan())
        self.assertEqual('D', accounts[1].get_status())

    def test_parse_master_accounts_supports_optional_plan_field(self) -> None:
        handler = FileHandler()
        content = (
            "00001 John Doe             A 01000.00 0003 SP\n"
            "00002 Jane Smith           A 00500.00 0010\n"
        )

        accounts = handler.parse_master_accounts_file(content)

        self.assertEqual(2, len(accounts))
        self.assertEqual(3, accounts[0].get_total_transactions())
        self.assertEqual(Account.STUDENT_PLAN, accounts[0].get_plan())
        self.assertEqual(Account.NON_STUDENT_PLAN, accounts[1].get_plan())


class TransactionFormatTests(unittest.TestCase):
    """Verify the updated transfer record preserves the full destination account."""

    def test_transfer_transaction_round_trips_with_full_destination_account(self) -> None:
        transaction = Transaction.create_transfer('John Doe', '1', '2', 100.0)
        line = transaction.to_file_string()

        parsed = Transaction.from_file_string(line)

        self.assertEqual(43, len(line))
        self.assertEqual('00001', parsed.account_number)
        self.assertEqual('00002', parsed.target_account)


class BatchProcessorTests(unittest.TestCase):
    """Verify account updates, fees, and constraint logging in the Back End."""

    def test_constraint_failures_are_logged_without_mutating_accounts(self) -> None:
        accounts = [Account('00001', 'John Doe', 'A', 50.0, total_transactions=0, plan=Account.STUDENT_PLAN)]
        processor = BatchProcessor(accounts)
        transactions = [
            Transaction.create_withdrawal('John Doe', '00001', 50.0),
            Transaction.create_account('Jane Smith', '00001', 100.0),
        ]

        messages = processor.process(transactions)
        remaining = processor.get_accounts()

        self.assertEqual(2, len(messages))
        self.assertIn('Negative balance prevented', messages[0])
        self.assertIn('Duplicate account creation prevented', messages[1])
        self.assertEqual(50.0, remaining[0].get_balance())
        self.assertEqual(0, remaining[0].get_total_transactions())

    def test_admin_maintenance_transactions_update_account_state(self) -> None:
        accounts = [
            Account('00001', 'John Doe', 'A', 100.0, total_transactions=1, plan=Account.STUDENT_PLAN),
            Account('00002', 'Jane Smith', 'A', 200.0, total_transactions=2, plan=Account.STUDENT_PLAN),
        ]
        processor = BatchProcessor(accounts)
        transactions = [
            Transaction.create_changeplan('John Doe', '00001'),
            Transaction.create_disable('Jane Smith', '00002'),
            Transaction.create_delete('Jane Smith', '00002'),
            Transaction.create_account('Bob Brown', '00003', 300.0),
        ]

        messages = processor.process(transactions)
        remaining = processor.get_accounts()

        self.assertEqual([], messages)
        self.assertEqual(['00001', '00003'], [account.get_account_number() for account in remaining])
        self.assertEqual(Account.NON_STUDENT_PLAN, remaining[0].get_plan())
        self.assertEqual(Account.STUDENT_PLAN, remaining[1].get_plan())


class BackendCliTests(unittest.TestCase):
    """Verify the dedicated Back End entry point produces the required output files."""

    def test_backend_cli_processes_merged_transactions_end_to_end(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        backend_main = repo_root / 'backend_main.py'
        old_master = (
            "00001 John Doe             A 01000.00 0003 SP\n"
            "00002 Jane Smith           A 00500.00 0001 NP\n"
        )
        merged_transactions = (
            "01 John Doe             00001 00100.00  \n"
            "04 Jane Smith           00002 00050.00  \n"
            "02 Jane Smith           00002 00020.0000001\n"
            "05 Bob Brown            00003 00100.00  \n"
            "08 Bob Brown            00003 00000.00  \n"
            "07 Jane Smith           00002 00000.00  \n"
            "00                      00000 00000.00  \n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            old_master_file = temp_path / 'old_master.txt'
            merged_file = temp_path / 'merged.atf'
            new_master_file = temp_path / 'new_master.txt'
            new_current_file = temp_path / 'new_current.txt'

            old_master_file.write_text(old_master, encoding='utf-8')
            merged_file.write_text(merged_transactions, encoding='utf-8')

            result = subprocess.run(
                [
                    sys.executable,
                    str(backend_main),
                    str(old_master_file),
                    str(merged_file),
                    str(new_master_file),
                    str(new_current_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual('', result.stdout)
            self.assertEqual('', result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertEqual(
                (
                    "00001 John Doe             A 00919.95 0004 SP\n"
                    "00002 Jane Smith           D 00529.80 0003 NP\n"
                    "00003 Bob Brown            A 00100.00 0000 NP\n"
                ),
                new_master_file.read_text(encoding='utf-8'),
            )
            self.assertEqual(
                (
                    "00001 John Doe             A 00919.95 SP\n"
                    "00002 Jane Smith           D 00529.80 NP\n"
                    "00003 Bob Brown            A 00100.00 NP\n"
                    "00000 END_OF_FILE          A 00000.00 NP\n"
                ),
                new_current_file.read_text(encoding='utf-8'),
            )

    def test_backend_cli_preserves_non_plan_master_style(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        backend_main = repo_root / 'backend_main.py'
        old_master = "00001 John Doe             A 01000.00 0003\n"
        merged_transactions = "04 John Doe             00001 00050.00  \n00                      00000 00000.00  \n"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            old_master_file = temp_path / 'old_master.txt'
            merged_file = temp_path / 'merged.atf'
            new_master_file = temp_path / 'new_master.txt'
            new_current_file = temp_path / 'new_current.txt'

            old_master_file.write_text(old_master, encoding='utf-8')
            merged_file.write_text(merged_transactions, encoding='utf-8')

            result = subprocess.run(
                [
                    sys.executable,
                    str(backend_main),
                    str(old_master_file),
                    str(merged_file),
                    str(new_master_file),
                    str(new_current_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(0, result.returncode)
            self.assertEqual("00001 John Doe             A 01049.90 0004\n", new_master_file.read_text(encoding='utf-8'))
            self.assertEqual(
                "00001 John Doe             A 01049.90\n00000 END_OF_FILE          A 00000.00\n",
                new_current_file.read_text(encoding='utf-8'),
            )


if __name__ == '__main__':
    unittest.main()
