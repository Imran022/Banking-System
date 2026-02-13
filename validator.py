"""Validation rules for Front End transactions."""

from account import Account


class Validator:
    """Applies business constraints to each transaction type."""

    MAX_WITHDRAWAL_STANDARD = 500.00
    MAX_TRANSFER_STANDARD = 1000.00
    MAX_PAYBILL_STANDARD = 2000.00
    MAX_ACCOUNT_BALANCE = 99999.99
    MAX_NAME_LENGTH = 20
    VALID_COMPANIES = {'EC', 'CQ', 'FI'}

    def validate_withdrawal(self, account: Account | None, amount: float, is_admin: bool, session_total: float) -> str | None:
        """Validate withdrawal constraints and return an error message when invalid."""
        if account is None:
            return 'Account not found.'
        if account.is_disabled():
            return 'Account is disabled.'
        if amount <= 0:
            return 'Amount must be positive.'
        if (not is_admin) and (session_total + amount > self.MAX_WITHDRAWAL_STANDARD):
            return f'Maximum withdrawal per session is ${self.MAX_WITHDRAWAL_STANDARD:.2f}.'
        if account.get_balance() < amount:
            return 'Insufficient funds.'
        return None

    def validate_transfer(self, source: Account | None, target: Account | None, amount: float, is_admin: bool, session_total: float) -> str | None:
        """Validate transfer constraints and return an error message when invalid."""
        if source is None:
            return 'Source account not found.'
        if target is None:
            return 'Destination account not found.'
        if source.is_disabled() or target.is_disabled():
            return 'Source or destination account is disabled.'
        if amount <= 0:
            return 'Amount must be positive.'
        if (not is_admin) and (session_total + amount > self.MAX_TRANSFER_STANDARD):
            return f'Maximum transfer per session is ${self.MAX_TRANSFER_STANDARD:.2f}.'
        if source.get_balance() < amount:
            return 'Insufficient funds in source account.'
        return None

    def validate_paybill(self, account: Account | None, amount: float, company: str, is_admin: bool, session_total: float) -> str | None:
        """Validate paybill constraints and return an error message when invalid."""
        if account is None:
            return 'Account not found.'
        if account.is_disabled():
            return 'Account is disabled.'
        if company not in self.VALID_COMPANIES:
            return 'Invalid company code. Valid codes: EC, CQ, FI.'
        if amount <= 0:
            return 'Amount must be positive.'
        if (not is_admin) and (session_total + amount > self.MAX_PAYBILL_STANDARD):
            return f'Maximum paybill per session is ${self.MAX_PAYBILL_STANDARD:.2f}.'
        if account.get_balance() < amount:
            return 'Insufficient funds.'
        return None

    @staticmethod
    def validate_deposit(account: Account | None, amount: float) -> str | None:
        """Validate deposit constraints and return an error message when invalid."""
        if account is None:
            return 'Account not found.'
        if account.is_disabled():
            return 'Account is disabled.'
        if amount <= 0:
            return 'Amount must be positive.'
        return None

    def validate_create(self, holder_name: str, initial_balance: float, account_exists: bool) -> str | None:
        """Validate account-creation constraints and return an error message when invalid."""
        if len(holder_name) > self.MAX_NAME_LENGTH:
            return f'Account holder name must be at most {self.MAX_NAME_LENGTH} characters.'
        if initial_balance < 0:
            return 'Initial balance cannot be negative.'
        if initial_balance > self.MAX_ACCOUNT_BALANCE:
            return f'Maximum account balance is ${self.MAX_ACCOUNT_BALANCE:.2f}.'
        if account_exists:
            return 'Account number already exists.'
        return None

    @staticmethod
    def validate_account_exists(account: Account | None) -> str | None:
        """Validate that an account lookup succeeded."""
        if account is None:
            return 'Account not found.'
        return None

    @staticmethod
    def validate_disable(account: Account | None) -> str | None:
        """Validate disable-account constraints and return an error when invalid."""
        if account is None:
            return 'Account not found.'
        if account.is_disabled():
            return 'Account is already disabled.'
        return None
