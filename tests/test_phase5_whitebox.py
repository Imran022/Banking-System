"""
Phase 5 - White Box Unit Tests
CSCI 3060U

Method 1 (Statement Coverage):  Validator.validate_withdrawal
Method 2 (Decision + Loop Coverage): BankingSystem._generate_account_number
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from account import Account
from banking_system import BankingSystem
from validator import Validator


def make_account(number='00001', name='John Doe', status='A',
                 balance=1000.00, plan=Account.NON_STUDENT_PLAN) -> Account:
    return Account(number, name, status, balance, total_transactions=0, plan=plan)


# ===========================================================================
# METHOD 1 — Statement Coverage

# ===========================================================================

class TestValidateWithdrawalStatementCoverage(unittest.TestCase):

    def setUp(self):
        self.v = Validator()

    def test_sc1_account_not_found(self):
        # S1: account is None
        result = self.v.validate_withdrawal(None, 100.0, False, 0.0)
        self.assertEqual('Account not found.', result)

    def test_sc2_account_disabled(self):
        # S2: account exists but is disabled
        acc = make_account(status='D')
        result = self.v.validate_withdrawal(acc, 100.0, False, 0.0)
        self.assertEqual('Account is disabled.', result)

    def test_sc3_amount_not_positive(self):
        # S3: negative amount
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, -5.0, False, 0.0)
        self.assertEqual('Amount must be positive.', result)

    def test_sc3b_amount_zero(self):
        # S3: amount of exactly 0
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 0.0, False, 0.0)
        self.assertEqual('Amount must be positive.', result)

    def test_sc4_session_limit_exceeded_standard(self):
        # S4: standard mode, 600 > 500 session limit
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 600.0, False, 0.0)
        self.assertIn('Maximum withdrawal', result)

    def test_sc4_admin_bypasses_session_limit(self):
        # S4: admin mode ignores session limit
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 600.0, True, 0.0)
        self.assertIsNone(result)

    def test_sc4c_cumulative_exactly_at_limit(self):
        # S4: 400 already withdrawn + 100 = exactly 500, should pass
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 100.0, False, 400.0)
        self.assertIsNone(result)

    def test_sc4d_cumulative_one_cent_over_limit(self):
        # S4: 400.01 already withdrawn + 100 = 500.01, should fail
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 100.0, False, 400.01)
        self.assertIn('Maximum withdrawal', result)

    def test_sc5_insufficient_funds(self):
        # S5: balance too low
        acc = make_account(balance=10.0)
        result = self.v.validate_withdrawal(acc, 50.0, False, 0.0)
        self.assertEqual('Insufficient funds.', result)

    def test_sc6_valid_withdrawal(self):
        # S6: all checks pass, should return None
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 50.0, False, 0.0)
        self.assertIsNone(result)

    def test_sc6b_cumulative_session_within_limit(self):
        # S6: 200 already withdrawn + 200 more = 400, within limit
        acc = make_account(balance=1000.0)
        result = self.v.validate_withdrawal(acc, 200.0, False, 200.0)
        self.assertIsNone(result)


# ===========================================================================
# METHOD 2 — Decision + Loop Coverage

# ===========================================================================

class TestGenerateAccountNumberDecisionLoop(unittest.TestCase):

    def _make_system_with_accounts(self, account_numbers: list) -> BankingSystem:
        bs = BankingSystem()
        bs.accounts = [make_account(number=n) for n in account_numbers]
        return bs

    def test_dl1_no_accounts_returns_00001(self):
        # Loop: 0 iterations
        bs = self._make_system_with_accounts([])
        result = bs._generate_account_number()
        self.assertEqual('00001', result)

    def test_dl2_single_account_increments(self):
        # Loop: 1 iteration, D1 True
        bs = self._make_system_with_accounts(['00005'])
        result = bs._generate_account_number()
        self.assertEqual('00006', result)

    def test_dl3_multiple_accounts_picks_max(self):
        # Loop: 3 iterations, D1 True then True then False
        bs = self._make_system_with_accounts(['00003', '00007', '00002'])
        result = bs._generate_account_number()
        self.assertEqual('00008', result)

    def test_dl4_descending_order_picks_first(self):
        # Loop: 2 iterations, D1 True then False
        bs = self._make_system_with_accounts(['00007', '00003'])
        result = bs._generate_account_number()
        self.assertEqual('00008', result)

    def test_dl5_non_numeric_account_skipped(self):
        # Loop: 1 iteration, except/continue path taken
        bs = self._make_system_with_accounts(['XXXXX'])
        result = bs._generate_account_number()
        self.assertEqual('00001', result)

    def test_dl6_mixed_numeric_and_non_numeric(self):
        # Loop: 3 iterations, numeric then non-numeric (skipped) then numeric
        bs = BankingSystem()
        bs.accounts = [
            make_account(number='00005'),
            make_account(number='XXXXX'),
            make_account(number='00009'),
        ]
        result = bs._generate_account_number()
        self.assertEqual('00010', result)

    def test_dl7_high_value_account(self):
        # Loop: 1 iteration, boundary value 99999
        bs = self._make_system_with_accounts(['99999'])
        result = bs._generate_account_number()
        self.assertEqual('100000', result)

    def test_dl8_all_non_numeric_returns_00001(self):
        # Loop: 2 iterations, both skip via except
        bs = BankingSystem()
        bs.accounts = [
            make_account(number='AAAAA'),
            make_account(number='BBBBB'),
        ]
        result = bs._generate_account_number()
        self.assertEqual('00001', result)

    def test_dl9_account_00001_increments_to_00002(self):
        # Loop: 1 iteration, D1 True
        bs = self._make_system_with_accounts(['00001'])
        result = bs._generate_account_number()
        self.assertEqual('00002', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)