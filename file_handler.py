"""Parse and write fixed-format Front End and Back End files."""

from account import Account
from transaction import Transaction


class FileHandler:
    """Handle Current Accounts, Master Accounts, and transaction text files."""

    @staticmethod
    def current_accounts_include_plan(file_content: str) -> bool:
        """Return True when current-account input lines include the optional plan field."""
        for line in file_content.splitlines():
            if not line.strip() or 'END_OF_FILE' in line:
                continue
            return len(line) >= 39
        return False

    @staticmethod
    def master_accounts_include_plan(file_content: str) -> bool:
        """Return True when master-account input lines include the optional plan field."""
        for line in file_content.splitlines():
            if not line.strip():
                continue
            return len(line) >= 44
        return False

    @staticmethod
    def read_file(file_path: str) -> str:
        """Read and return entire text file contents."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_file(content: str, file_path: str) -> None:
        """Write text content to file using UTF-8 encoding."""
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            file.write(content)

    def parse_accounts_file(self, file_content: str) -> list[Account]:
        """Parse Current Bank Accounts file text into account objects."""
        return self.parse_current_accounts_file(file_content)

    def parse_current_accounts_file(self, file_content: str) -> list[Account]:
        """Parse Current Bank Accounts file text into account objects."""
        accounts: list[Account] = []
        for line_number, line in enumerate(file_content.splitlines(), start=1):
            if not line.strip():
                continue
            if 'END_OF_FILE' in line:
                break
            if len(line) < 37:
                raise ValueError(f'Current accounts line {line_number} is too short: {len(line)}')

            account_number = line[0:5].strip()
            holder_name = line[6:26].strip()
            status = line[27:28].strip()
            balance_text = line[29:37].strip()
            plan = line[38:].strip() if len(line) >= 39 else Account.NON_STUDENT_PLAN

            try:
                balance = float(balance_text)
            except ValueError as exc:
                raise ValueError(
                    f'Current accounts line {line_number} has invalid balance "{balance_text}".'
                ) from exc

            accounts.append(Account(account_number, holder_name, status, balance, plan=plan or Account.NON_STUDENT_PLAN))

        return accounts

    def parse_master_accounts_file(self, file_content: str) -> list[Account]:
        """Parse Master Bank Accounts file text into account objects."""
        accounts: list[Account] = []
        for line_number, line in enumerate(file_content.splitlines(), start=1):
            if not line.strip():
                continue
            if len(line) < 42:
                raise ValueError(f'Master accounts line {line_number} is too short: {len(line)}')

            account_number = line[0:5].strip()
            holder_name = line[6:26].strip()
            status = line[27:28].strip()
            balance_text = line[29:37].strip()
            transaction_count_text = line[38:42].strip()
            plan = line[43:].strip() if len(line) >= 44 else Account.NON_STUDENT_PLAN

            try:
                balance = float(balance_text)
                transaction_count = int(transaction_count_text)
            except ValueError as exc:
                raise ValueError(
                    f'Master accounts line {line_number} has invalid numeric fields.'
                ) from exc

            accounts.append(
                Account(
                    account_number,
                    holder_name,
                    status,
                    balance,
                    total_transactions=transaction_count,
                    plan=plan or Account.NON_STUDENT_PLAN,
                )
            )

        return accounts

    @staticmethod
    def parse_transaction_file(file_content: str) -> list[Transaction]:
        """Parse a merged transaction file into transaction objects."""
        transactions: list[Transaction] = []
        for line_number, line in enumerate(file_content.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                transactions.append(Transaction.from_file_string(line))
            except ValueError as exc:
                raise ValueError(f'Transaction line {line_number}: {exc}') from exc
        return transactions

    @staticmethod
    def generate_transaction_file(transactions: list[Transaction]) -> str:
        """Serialize all session transactions plus end-of-session marker."""
        lines = [transaction.to_file_string() for transaction in transactions]
        lines.append(Transaction.create_end_session().to_file_string())
        return '\n'.join(lines) + '\n'

    @staticmethod
    def generate_current_accounts_file(accounts: list[Account], include_plan: bool = True) -> str:
        """Serialize current-account output sorted by account number with EOF marker."""
        ordered_accounts = sorted(accounts, key=lambda account: account.get_account_number())
        lines = [account.to_current_file_string(include_plan=include_plan) for account in ordered_accounts]
        eof_account = Account('00000', 'END_OF_FILE', 'A', 0.0, plan=Account.NON_STUDENT_PLAN)
        lines.append(eof_account.to_current_file_string(include_plan=include_plan))
        return '\n'.join(lines) + '\n'

    @staticmethod
    def generate_master_accounts_file(accounts: list[Account], include_plan: bool = True) -> str:
        """Serialize master-account output sorted by account number."""
        ordered_accounts = sorted(accounts, key=lambda account: account.get_account_number())
        lines = [account.to_master_file_string(include_plan=include_plan) for account in ordered_accounts]
        return '\n'.join(lines) + '\n'
