"""
Phase 5 - White Box Unit Tests
CSCI 3060U

Method 1 (Statement Coverage): BatchProcessor._apply_create
Method 2 (Decision + Loop Coverage): FileHandler.parse_master_accounts_file
"""

import unittest

from account import Account
from batch_processor import BatchProcessor
from file_handler import FileHandler
from transaction import Transaction


def make_account(
    number: str = '00001',
    name: str = 'John Doe',
    status: str = 'A',
    balance: float = 1000.00,
    total_transactions: int = 0,
    plan: str = Account.NON_STUDENT_PLAN,
) -> Account:
    return Account(number, name, status, balance, total_transactions=total_transactions, plan=plan)


def make_master_line(
    account_number: str,
    holder_name: str,
    status: str,
    balance: float,
    total_transactions: int,
    plan: str | None = None,
) -> str:
    base = (
        f"{str(account_number).zfill(5)} "
        f"{holder_name.ljust(20)[:20]} "
        f"{status} "
        f"{balance:08.2f} "
        f"{str(total_transactions).zfill(4)}"
    )
    if plan is None:
        return base
    return f"{base} {plan}"


class TestApplyCreateStatementCoverage(unittest.TestCase):
    """Statement coverage for the Back End create-account handler."""

    def test_sc1_duplicate_account_creation_logs_constraint(self) -> None:
        processor = BatchProcessor([make_account(number='00001', name='Existing User', balance=500.0)])

        processor._apply_create(Transaction.create_account('Jane Smith', '00001', 100.0))

        self.assertEqual(1, len(processor.failed_constraints))
        self.assertIn('Duplicate account creation prevented for account 00001', processor.failed_constraints[0])
        self.assertEqual(['00001'], sorted(processor.accounts_by_number.keys()))
        self.assertEqual('Existing User', processor.accounts_by_number['00001'].get_holder_name())

    def test_sc2_new_account_is_created_with_backend_defaults(self) -> None:
        processor = BatchProcessor([make_account(number='00001', name='Existing User', balance=500.0)])

        processor._apply_create(Transaction.create_account('Jane Smith', '00002', 150.0))

        self.assertEqual([], processor.failed_constraints)
        self.assertEqual(['00001', '00002'], sorted(processor.accounts_by_number.keys()))
        created = processor.accounts_by_number['00002']
        self.assertEqual('Jane Smith', created.get_holder_name())
        self.assertEqual('A', created.get_status())
        self.assertEqual(150.0, created.get_balance())
        self.assertEqual(0, created.get_total_transactions())
        self.assertEqual(Account.STUDENT_PLAN, created.get_plan())


class TestParseMasterAccountsDecisionLoopCoverage(unittest.TestCase):
    """Decision and loop coverage for Back End master-account parsing."""

    def setUp(self) -> None:
        self.handler = FileHandler()

    def test_dl1_empty_file_returns_no_accounts(self) -> None:
        accounts = self.handler.parse_master_accounts_file('')
        self.assertEqual([], accounts)

    def test_dl2_single_valid_record_without_plan(self) -> None:
        content = make_master_line('00001', 'John Doe', 'A', 1000.0, 3) + '\n'

        accounts = self.handler.parse_master_accounts_file(content)

        self.assertEqual(1, len(accounts))
        self.assertEqual('00001', accounts[0].get_account_number())
        self.assertEqual(Account.NON_STUDENT_PLAN, accounts[0].get_plan())
        self.assertEqual(3, accounts[0].get_total_transactions())

    def test_dl3_multiple_records_with_blank_line_and_optional_plan(self) -> None:
        content = (
            make_master_line('00001', 'John Doe', 'A', 1000.0, 3, Account.STUDENT_PLAN) + '\n'
            '\n'
            + make_master_line('00002', 'Jane Smith', 'D', 500.0, 12) + '\n'
        )

        accounts = self.handler.parse_master_accounts_file(content)

        self.assertEqual(2, len(accounts))
        self.assertEqual(Account.STUDENT_PLAN, accounts[0].get_plan())
        self.assertEqual(Account.NON_STUDENT_PLAN, accounts[1].get_plan())
        self.assertEqual('D', accounts[1].get_status())

    def test_dl4_short_record_raises_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, 'too short'):
            self.handler.parse_master_accounts_file('short line\n')

    def test_dl5_invalid_numeric_fields_raise_value_error(self) -> None:
        invalid = "00001 John Doe             A X1000.00 0003\n"

        with self.assertRaisesRegex(ValueError, 'invalid numeric fields'):
            self.handler.parse_master_accounts_file(invalid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
