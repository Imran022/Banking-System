"""Account entity shared by the Front End and Back End."""


class Account:
    """Store bank account state, including Phase 4 master-file metadata."""

    STUDENT_PLAN = 'SP'
    NON_STUDENT_PLAN = 'NP'

    def __init__(
        self,
        account_number: str,
        holder_name: str,
        status: str,
        balance: float,
        total_transactions: int = 0,
        plan: str = NON_STUDENT_PLAN,
    ) -> None:
        """Initialize one account instance from current or master account fields."""
        self.account_number = str(account_number).zfill(5)
        self.holder_name = holder_name
        self.status = status
        self.balance = float(balance)
        self.total_transactions = int(total_transactions)
        self.plan = plan or self.NON_STUDENT_PLAN

    def get_account_number(self) -> str:
        """Return the account number."""
        return self.account_number

    def get_holder_name(self) -> str:
        """Return the account holder name."""
        return self.holder_name

    def get_status(self) -> str:
        """Return the current account status."""
        return self.status

    def is_disabled(self) -> bool:
        """Return True when account status is disabled."""
        return self.status == 'D'

    def disable(self) -> None:
        """Set account status to disabled."""
        self.status = 'D'

    def get_balance(self) -> float:
        """Return the current account balance."""
        return self.balance

    def get_total_transactions(self) -> int:
        """Return the total transaction count used in master-file output."""
        return self.total_transactions

    def increment_total_transactions(self, count: int = 1) -> None:
        """Increase the total transaction count by the provided amount."""
        self.total_transactions += count

    def get_plan(self) -> str:
        """Return the current account payment plan."""
        return self.plan

    def set_plan(self, plan: str) -> None:
        """Set the account payment plan."""
        self.plan = plan

    def is_student_plan(self) -> bool:
        """Return True when the account uses the student payment plan."""
        return self.plan == self.STUDENT_PLAN

    def transaction_fee(self) -> float:
        """Return the per-transaction fee associated with the current plan."""
        return 0.05 if self.is_student_plan() else 0.10

    def withdraw(self, amount: float) -> bool:
        """Attempt withdrawal and return whether it succeeded."""
        if self.balance < amount:
            return False
        self.balance -= amount
        return True

    def deposit(self, amount: float) -> None:
        """Apply a deposit to current in-memory balance."""
        self.balance += amount

    def to_current_file_string(self, include_plan: bool = True) -> str:
        """Format this account as one fixed-width Current Accounts file line."""
        account_num = self.account_number.zfill(5)
        name = self.holder_name.ljust(20)[:20]
        balance = f"{self.balance:08.2f}"
        if include_plan:
            return f"{account_num} {name} {self.status} {balance} {self.plan}"
        return f"{account_num} {name} {self.status} {balance}"

    def to_master_file_string(self, include_plan: bool = True) -> str:
        """Format this account as one fixed-width Master Accounts file line."""
        account_num = self.account_number.zfill(5)
        name = self.holder_name.ljust(20)[:20]
        balance = f"{self.balance:08.2f}"
        transactions = str(self.total_transactions).zfill(4)
        if include_plan:
            return f"{account_num} {name} {self.status} {balance} {transactions} {self.plan}"
        return f"{account_num} {name} {self.status} {balance} {transactions}"

    def to_file_string(self) -> str:
        """Format this account using the current-account file layout."""
        return self.to_current_file_string(include_plan=True)
