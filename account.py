"""Account entity used by the Front End session."""


class Account:
    """Stores account number, holder name, status, and balance."""

    def __init__(self, account_number: str, holder_name: str, status: str, balance: float) -> None:
        """Initialize one account instance from current accounts file fields."""
        self.account_number = str(account_number)
        self.holder_name = holder_name
        self.status = status
        self.balance = float(balance)

    def get_account_number(self) -> str:
        """Return the account number."""
        return self.account_number

    def get_holder_name(self) -> str:
        """Return the account holder name."""
        return self.holder_name

    def is_disabled(self) -> bool:
        """Return True when account status is disabled."""
        return self.status == 'D'

    def disable(self) -> None:
        """Set account status to disabled."""
        self.status = 'D'

    def get_balance(self) -> float:
        """Return the current account balance."""
        return self.balance

    def withdraw(self, amount: float) -> bool:
        """Attempt withdrawal and return whether it succeeded."""
        if self.balance < amount:
            return False
        self.balance -= amount
        return True

    def deposit(self, amount: float) -> None:
        """Apply a deposit to current in-memory balance."""
        self.balance += amount

    def to_file_string(self) -> str:
        """Format this account as one fixed-width Current Accounts file line."""
        account_num = self.account_number.zfill(5)
        name = self.holder_name.ljust(20)[:20]
        balance = f"{self.balance:.2f}".zfill(8)
        return f"{account_num} {name} {self.status} {balance}"
