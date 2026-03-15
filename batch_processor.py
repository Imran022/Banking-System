"""Overnight batch processor for applying merged banking transactions."""

from account import Account
from transaction import Transaction


class BatchProcessor:
    """Apply merged transaction records to a prior master account snapshot."""

    def __init__(self, accounts: list[Account]) -> None:
        """Initialize the processor with an in-memory account index."""
        self.accounts_by_number = {
            account.get_account_number(): account
            for account in accounts
        }
        self.failed_constraints: list[str] = []

    def process(self, transactions: list[Transaction]) -> list[str]:
        """Apply each merged transaction in order and return logged constraint messages."""
        for transaction in transactions:
            if transaction.code == Transaction.CODES['END_SESSION']:
                continue
            self._apply_transaction(transaction)
        return self.failed_constraints

    def get_accounts(self) -> list[Account]:
        """Return all remaining accounts after batch processing."""
        return sorted(self.accounts_by_number.values(), key=lambda account: account.get_account_number())

    def _apply_transaction(self, transaction: Transaction) -> None:
        """Dispatch one transaction record to its handler."""
        handlers = {
            Transaction.CODES['WITHDRAWAL']: self._apply_withdrawal,
            Transaction.CODES['TRANSFER']: self._apply_transfer,
            Transaction.CODES['PAYBILL']: self._apply_paybill,
            Transaction.CODES['DEPOSIT']: self._apply_deposit,
            Transaction.CODES['CREATE']: self._apply_create,
            Transaction.CODES['DELETE']: self._apply_delete,
            Transaction.CODES['DISABLE']: self._apply_disable,
            Transaction.CODES['CHANGEPLAN']: self._apply_changeplan,
        }
        handler = handlers.get(transaction.code)
        if handler is None:
            raise ValueError(f'Fatal error - Unsupported transaction code {transaction.code}.')
        handler(transaction)

    def _apply_withdrawal(self, transaction: Transaction) -> None:
        """Apply a withdrawal plus the account's daily transaction fee."""
        account = self._require_account(transaction.account_number, transaction.account_holder_name)
        fee = account.transaction_fee()
        projected_balance = account.get_balance() - transaction.amount - fee
        if projected_balance < 0:
            self._log_constraint(
                f'Negative balance prevented for withdrawal on account {account.get_account_number()}',
                transaction,
            )
            return
        account.withdraw(transaction.amount + fee)
        account.increment_total_transactions()

    def _apply_transfer(self, transaction: Transaction) -> None:
        """Apply a transfer from the source account to the destination account."""
        source = self._require_account(transaction.account_number, transaction.account_holder_name)
        if not transaction.target_account:
            raise ValueError('Fatal error - Merged transaction file - Transfer is missing destination account.')
        target = self._require_account(transaction.target_account)
        fee = source.transaction_fee()
        projected_balance = source.get_balance() - transaction.amount - fee
        if projected_balance < 0:
            self._log_constraint(
                f'Negative balance prevented for transfer on account {source.get_account_number()}',
                transaction,
            )
            return
        source.withdraw(transaction.amount + fee)
        target.deposit(transaction.amount)
        source.increment_total_transactions()

    def _apply_paybill(self, transaction: Transaction) -> None:
        """Apply a paybill transaction plus the account's daily transaction fee."""
        account = self._require_account(transaction.account_number, transaction.account_holder_name)
        fee = account.transaction_fee()
        projected_balance = account.get_balance() - transaction.amount - fee
        if projected_balance < 0:
            self._log_constraint(
                f'Negative balance prevented for paybill on account {account.get_account_number()}',
                transaction,
            )
            return
        account.withdraw(transaction.amount + fee)
        account.increment_total_transactions()

    def _apply_deposit(self, transaction: Transaction) -> None:
        """Apply a deposit and then charge the account's daily transaction fee."""
        account = self._require_account(transaction.account_number, transaction.account_holder_name)
        fee = account.transaction_fee()
        projected_balance = account.get_balance() + transaction.amount - fee
        if projected_balance < 0:
            self._log_constraint(
                f'Negative balance prevented for deposit on account {account.get_account_number()}',
                transaction,
            )
            return
        account.deposit(transaction.amount - fee)
        account.increment_total_transactions()

    def _apply_create(self, transaction: Transaction) -> None:
        """Create a new account unless the requested account number already exists."""
        account_number = transaction.account_number
        if account_number in self.accounts_by_number:
            self._log_constraint(
                f'Duplicate account creation prevented for account {account_number}',
                transaction,
            )
            return
        self.accounts_by_number[account_number] = Account(
            account_number,
            transaction.account_holder_name,
            'A',
            transaction.amount,
            total_transactions=0,
            plan=Account.STUDENT_PLAN,
        )

    def _apply_delete(self, transaction: Transaction) -> None:
        """Delete an existing account from the new master and current snapshots."""
        account = self._require_account(transaction.account_number, transaction.account_holder_name)
        del self.accounts_by_number[account.get_account_number()]

    def _apply_disable(self, transaction: Transaction) -> None:
        """Disable an existing account."""
        account = self._require_account(transaction.account_number, transaction.account_holder_name)
        account.disable()

    def _apply_changeplan(self, transaction: Transaction) -> None:
        """Set an account's payment plan to non-student."""
        account = self._require_account(transaction.account_number, transaction.account_holder_name)
        account.set_plan(Account.NON_STUDENT_PLAN)

    def _require_account(self, account_number: str, holder_name: str | None = None) -> Account:
        """Return the referenced account or raise a fatal error for impossible input."""
        account = self.accounts_by_number.get(str(account_number).zfill(5))
        if account is None:
            raise ValueError(f'Fatal error - Account {str(account_number).zfill(5)} not found.')
        if holder_name is not None and account.get_holder_name() != holder_name:
            raise ValueError(
                f'Fatal error - Account holder mismatch for account {account.get_account_number()}.'
            )
        return account

    def _log_constraint(self, description: str, transaction: Transaction) -> None:
        """Record a non-fatal failed business constraint for the current transaction."""
        self.failed_constraints.append(
            f'ERROR: Constraint violation - {description} - Transaction: {transaction.to_file_string()}'
        )
