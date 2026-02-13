"""Parses and writes fixed-format Front End files."""

from account import Account
from transaction import Transaction


class FileHandler:
    """Handles Current Bank Accounts and transaction output text files."""

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
        accounts: list[Account] = []
        for line in file_content.splitlines():
            if not line.strip():
                continue
            if 'END_OF_FILE' in line:
                break
            if len(line) < 37:
                continue

            account_number = line[0:5].strip()
            holder_name = line[6:26].strip()
            status = line[27:28].strip()
            balance_text = line[29:37].strip()

            try:
                balance = float(balance_text)
            except ValueError:
                continue

            accounts.append(Account(account_number, holder_name, status, balance))

        return accounts

    @staticmethod
    def generate_transaction_file(transactions: list[Transaction]) -> str:
        """Serialize all session transactions plus end-of-session marker."""
        lines = [transaction.to_file_string() for transaction in transactions]
        lines.append(Transaction.create_end_session().to_file_string())
        return '\n'.join(lines) + '\n'
