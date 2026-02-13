"""Core transaction controller for the Front End console prototype."""

from account import Account
from file_handler import FileHandler
from transaction import Transaction
from validator import Validator


class BankingSystem:
    """Owns account/session state and applies Front End transactions."""

    def __init__(self) -> None:
        """Initialize dependencies, in-memory account state, and session totals."""
        self.file_handler = FileHandler()
        self.validator = Validator()
        self.accounts: list[Account] = []
        self.transactions: list[Transaction] = []

        self.is_logged_in = False
        self.is_admin = False
        self.current_user: str | None = None

        self.session_withdrawals = 0.0
        self.session_transfers = 0.0
        self.session_paybills = 0.0

    def load_accounts(self, file_content: str) -> None:
        """Load accounts from Current Bank Accounts file contents."""
        self.accounts = self.file_handler.parse_accounts_file(file_content)

    def get_accounts(self) -> list[Account]:
        """Return the currently loaded account list."""
        return self.accounts

    def session_status(self) -> dict[str, object]:
        """Return session mode and current user state."""
        return {
            'is_logged_in': self.is_logged_in,
            'is_admin': self.is_admin,
            'current_user': self.current_user,
        }

    def find_account_by_number(self, account_number: str) -> Account | None:
        """Find any account by account number."""
        for account in self.accounts:
            if account.get_account_number() == str(account_number):
                return account
        return None

    def find_user_account(self, holder_name: str, account_number: str) -> Account | None:
        """Find an account by holder name plus account number"""
        for account in self.accounts:
            if account.get_holder_name() == holder_name and account.get_account_number() == str(account_number):
                return account
        return None

    def process_login(self, mode: str, user_name: str | None = None) -> tuple[bool, str]:
        """Process login transaction and enforce login mode rules."""
        if self.is_logged_in:
            return False, 'Already logged in. Please logout first.'

        if mode == 'admin':
            self.is_logged_in = True
            self.is_admin = True
            self.current_user = 'Admin'
            return True, 'Admin session started.'

        if mode == 'standard':
            if not user_name:
                return False, 'Account holder name required for standard login.'
            self.is_logged_in = True
            self.is_admin = False
            self.current_user = user_name
            return True, f'Standard user {user_name} logged in.'

        return False, 'Invalid login mode. Use "standard" or "admin".'

    def process_logout(self) -> tuple[bool, str]:
        """Process logout and reset per-session tracking totals."""
        if not self.is_logged_in:
            return False, 'Not logged in.'

        self.is_logged_in = False
        self.is_admin = False
        self.current_user = None
        self.session_withdrawals = 0.0
        self.session_transfers = 0.0
        self.session_paybills = 0.0

        return True, 'Session ended. Transaction file ready for download.'

    def process_withdrawal(self, account_number: str, amount: float, holder_name: str | None = None) -> tuple[bool, str]:
        """Process withdrawal and append successful transaction output record."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'

        owner = holder_name if self.is_admin else (self.current_user or '')
        account = self.find_user_account(owner, account_number)
        error = self.validator.validate_withdrawal(account, amount, self.is_admin, self.session_withdrawals)
        if error:
            return False, error

        account.withdraw(amount)
        self.session_withdrawals += amount
        self.transactions.append(Transaction.create_withdrawal(owner, account_number, amount))
        return True, f'Withdrawal of ${amount:.2f} successful. New balance: ${account.get_balance():.2f}'

    def process_transfer(self, source_number: str, target_number: str, amount: float, holder_name: str | None = None) -> tuple[bool, str]:
        """Process transfer and append successful transaction output record."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'

        owner = holder_name if self.is_admin else (self.current_user or '')
        source = self.find_user_account(owner, source_number)
        target = self.find_account_by_number(target_number)
        error = self.validator.validate_transfer(source, target, amount, self.is_admin, self.session_transfers)
        if error:
            return False, error

        source.withdraw(amount)
        target.deposit(amount)
        self.session_transfers += amount
        self.transactions.append(Transaction.create_transfer(owner, source_number, target_number, amount))
        return True, f'Transfer of ${amount:.2f} successful.'

    def process_paybill(self, account_number: str, amount: float, company: str, holder_name: str | None = None) -> tuple[bool, str]:
        """Process paybill and append successful transaction output record."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'

        owner = holder_name if self.is_admin else (self.current_user or '')
        account = self.find_user_account(owner, account_number)
        error = self.validator.validate_paybill(account, amount, company, self.is_admin, self.session_paybills)
        if error:
            return False, error

        account.withdraw(amount)
        self.session_paybills += amount
        self.transactions.append(Transaction.create_paybill(owner, account_number, amount, company))
        return True, f'Bill payment of ${amount:.2f} to {company} successful.'

    def process_deposit(self, account_number: str, amount: float, holder_name: str | None = None) -> tuple[bool, str]:
        """Process deposit request and append transaction for next-session effect."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'

        owner = holder_name if self.is_admin else (self.current_user or '')
        account = self.find_user_account(owner, account_number)
        error = self.validator.validate_deposit(account, amount)
        if error:
            return False, error

        self.transactions.append(Transaction.create_deposit(owner, account_number, amount))
        return True, f'Deposit of ${amount:.2f} accepted (available next session).'

    def process_create(self, holder_name: str, initial_balance: float) -> tuple[bool, str]:
        """Process privileged create-account request."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'
        if not self.is_admin:
            return False, 'Create account is a privileged transaction. Admin access required.'

        new_number = self._generate_account_number()
        exists = self.find_account_by_number(new_number) is not None
        error = self.validator.validate_create(holder_name, initial_balance, exists)
        if error:
            return False, error

        self.transactions.append(Transaction.create_account(holder_name, new_number, initial_balance))
        return True, f'Account {new_number} created for {holder_name} (available next session).'

    def process_delete(self, holder_name: str, account_number: str) -> tuple[bool, str]:
        """Process privileged delete-account request."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'
        if not self.is_admin:
            return False, 'Delete account is a privileged transaction. Admin access required.'

        account = self.find_user_account(holder_name, account_number)
        error = self.validator.validate_account_exists(account)
        if error:
            return False, error

        self.accounts = [a for a in self.accounts if not (a.get_holder_name() == holder_name and a.get_account_number() == account_number)]
        self.transactions.append(Transaction.create_delete(holder_name, account_number))
        return True, f'Account {account_number} for {holder_name} deleted.'

    def process_disable(self, holder_name: str, account_number: str) -> tuple[bool, str]:
        """Process privileged disable-account request."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'
        if not self.is_admin:
            return False, 'Disable account is a privileged transaction. Admin access required.'

        account = self.find_user_account(holder_name, account_number)
        error = self.validator.validate_disable(account)
        if error:
            return False, error

        account.disable()
        self.transactions.append(Transaction.create_disable(holder_name, account_number))
        return True, f'Account {account_number} for {holder_name} disabled.'

    def process_changeplan(self, holder_name: str, account_number: str) -> tuple[bool, str]:
        """Process privileged changeplan request."""
        if not self.is_logged_in:
            return False, 'Must be logged in to perform transactions.'
        if not self.is_admin:
            return False, 'Change plan is a privileged transaction. Admin access required.'

        account = self.find_user_account(holder_name, account_number)
        error = self.validator.validate_account_exists(account)
        if error:
            return False, error

        self.transactions.append(Transaction.create_changeplan(holder_name, account_number))
        return True, f'Payment plan changed for account {account_number}.'

    def generate_transaction_file(self) -> str:
        """Generate full output transaction file content for the current session."""
        return self.file_handler.generate_transaction_file(self.transactions)

    def _generate_account_number(self) -> str:
        """Generate the next sequential account number from loaded accounts."""
        max_number = 0
        for account in self.accounts:
            try:
                value = int(account.get_account_number())
            except ValueError:
                continue
            if value > max_number:
                max_number = value
        return str(max_number + 1).zfill(5)
