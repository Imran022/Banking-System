"""Front End console prototype for CSCI 3060U Phase 2.

Program intention:
- Read the Current Bank Accounts file after login mode selection.
- Process Front End transaction commands from standard input.
- Write a Bank Account Transaction file at logout.

Input files:
- Current Bank Accounts File (fixed-width account records).

Output files:
- Bank Account Transaction File for the session date.
 
Run:
    python main.py
"""

from datetime import datetime

from banking_system import BankingSystem
from file_handler import FileHandler


class BankingConsole:
    """Console interface for session commands and guided transaction prompts."""

    def __init__(self) -> None:
        """Initialize controller and in-progress prompt-flow state."""
        self.system = BankingSystem()
        self.current_flow: str | None = None
        self.flow_data: dict[str, str] = {}

    @staticmethod
    def out(message: str) -> None:
        """Print a normal output message."""
        print(message)

    @staticmethod
    def err(message: str) -> None:
        """Print an error output message."""
        print(f'ERROR: {message}')

    def run(self) -> None:
        """Run command input loop and guided transaction/login flows."""
        self.out('Banking System Front End (Console)')
        self.out('Enter "login" to start a session.')
        while True:
            try:
                text = input('> ').strip()
            except EOFError:
                self.out('Exiting.')
                return

            if not text:
                continue
            if self.current_flow:
                self.handle_flow_input(text)
                continue
            self.handle_command(text.lower())

    def load_accounts(self) -> bool:
        """Prompt for and load the Current Bank Accounts input file."""
        path = input('Enter path to Current Bank Accounts file: ').strip()
        if not path:
            self.err('No file path provided.')
            return False

        try:
            content = FileHandler.read_file(path)
        except Exception as exc:
            self.err(f'Error loading file: {exc}')
            return False

        self.system.load_accounts(content)
        self.out(f'Loaded {len(self.system.get_accounts())} accounts.')
        return True

    def handle_command(self, command: str) -> None:
        """Handle top-level commands when no guided prompt flow is active."""
        if command == 'login':
            if self.system.session_status()['is_logged_in']:
                self.err('Already logged in. Please logout first.')
                return
            self.current_flow = 'login_mode'
            self.out('Enter session type (standard/admin):')
            return

        if command == 'logout':
            ok, msg = self.system.process_logout()
            if not ok:
                self.err(msg)
                return
            self.out(msg)
            self.write_transaction_file()
            return
        if command in {'withdrawal', 'withdraw', 'transfer', 'paybill', 'deposit', 'create', 'delete', 'disable', 'changeplan'}:
            self.start_transaction_flow(command)
            return

        self.err('Invalid command. Use login, logout, withdrawal, transfer, paybill, deposit, create, delete, disable, changeplan.')

    def start_transaction_flow(self, command: str) -> None:
        """Start guided data-entry prompts for the selected transaction code."""
        status = self.system.session_status()
        if not status['is_logged_in']:
            self.err('Must be logged in to perform transactions.')
            return
        tx = 'withdrawal' if command == 'withdraw' else command
        self.current_flow = tx
        self.flow_data = {}
        is_admin = bool(status['is_admin'])
        if tx == 'withdrawal':
            self.current_flow = 'withdrawal_name' if is_admin else 'withdrawal_account'
            self.out('Enter account holder name:' if is_admin else 'Enter account number:')
        elif tx == 'transfer':
            self.current_flow = 'transfer_name' if is_admin else 'transfer_source'
            self.out('Enter account holder name:' if is_admin else 'Enter source account number:')
        elif tx == 'paybill':
            self.current_flow = 'paybill_name' if is_admin else 'paybill_account'
            self.out('Enter account holder name:' if is_admin else 'Enter account number:')
        elif tx == 'deposit':
            self.current_flow = 'deposit_name' if is_admin else 'deposit_account'
            self.out('Enter account holder name:' if is_admin else 'Enter account number:')
        elif tx == 'create':
            self.current_flow = 'create_name'
            self.out('Enter new account holder name:')
        elif tx == 'delete':
            self.current_flow = 'delete_name'
            self.out('Enter account holder name:')
        elif tx == 'disable':
            self.current_flow = 'disable_name'
            self.out('Enter account holder name:')
        elif tx == 'changeplan':
            self.current_flow = 'changeplan_name'
            self.out('Enter account holder name:')

    def handle_flow_input(self, text: str) -> None:
        """Handle one input line while in login or transaction prompt flow."""
        flow = self.current_flow
        if flow == 'login_mode':
            mode = text.lower()
            if mode == 'admin':
                if not self.load_accounts():
                    self.current_flow = None
                    return
                ok, msg = self.system.process_login('admin')
                self.out(msg) if ok else self.err(msg)
                self.current_flow = None
            elif mode == 'standard':
                self.current_flow = 'login_name'
                self.out('Enter account holder name:')
            else:
                self.err('Invalid mode. Use standard or admin.')
            return

        if flow == 'login_name':
            if not self.load_accounts():
                self.current_flow = None
                return
            ok, msg = self.system.process_login('standard', text)
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        self.handle_transaction_flow(text)

    def handle_transaction_flow(self, text: str) -> None:
        """Handle one input line for any in-progress transaction prompt sequence."""
        flow = self.current_flow
        if flow == 'withdrawal_name':
            self.flow_data['name'] = text
            self.current_flow = 'withdrawal_account'
            self.out('Enter account number:')
            return
        if flow == 'withdrawal_account':
            self.flow_data['account'] = text
            self.current_flow = 'withdrawal_amount'
            self.out('Enter amount to withdraw:')
            return
        if flow == 'withdrawal_amount':
            amount = self.parse_positive_amount(text)
            if amount is None:
                self.err('Invalid amount. Enter a positive number.')
                return
            ok, msg = self.system.process_withdrawal(self.flow_data['account'], amount, self.flow_data.get('name'))
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow == 'transfer_name':
            self.flow_data['name'] = text
            self.current_flow = 'transfer_source'
            self.out('Enter source account number:')
            return
        if flow == 'transfer_source':
            self.flow_data['source'] = text
            self.current_flow = 'transfer_target'
            self.out('Enter destination account number:')
            return
        if flow == 'transfer_target':
            self.flow_data['target'] = text
            self.current_flow = 'transfer_amount'
            self.out('Enter amount to transfer:')
            return
        if flow == 'transfer_amount':
            amount = self.parse_positive_amount(text)
            if amount is None:
                self.err('Invalid amount. Enter a positive number.')
                return
            ok, msg = self.system.process_transfer(
                self.flow_data['source'],
                self.flow_data['target'],
                amount,
                self.flow_data.get('name'),
            )
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow == 'paybill_name':
            self.flow_data['name'] = text
            self.current_flow = 'paybill_account'
            self.out('Enter account number:')
            return
        if flow == 'paybill_account':
            self.flow_data['account'] = text
            self.current_flow = 'paybill_company'
            self.out('Enter company code (EC, CQ, FI):')
            return
        if flow == 'paybill_company':
            self.flow_data['company'] = text.upper()
            self.current_flow = 'paybill_amount'
            self.out('Enter amount to pay:')
            return
        if flow == 'paybill_amount':
            amount = self.parse_positive_amount(text)
            if amount is None:
                self.err('Invalid amount. Enter a positive number.')
                return
            ok, msg = self.system.process_paybill(
                self.flow_data['account'],
                amount,
                self.flow_data['company'],
                self.flow_data.get('name'),
            )
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow == 'deposit_name':
            self.flow_data['name'] = text
            self.current_flow = 'deposit_account'
            self.out('Enter account number:')
            return
        if flow == 'deposit_account':
            self.flow_data['account'] = text
            self.current_flow = 'deposit_amount'
            self.out('Enter amount to deposit:')
            return
        if flow == 'deposit_amount':
            amount = self.parse_positive_amount(text)
            if amount is None:
                self.err('Invalid amount. Enter a positive number.')
                return
            ok, msg = self.system.process_deposit(self.flow_data['account'], amount, self.flow_data.get('name'))
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow == 'create_name':
            self.flow_data['name'] = text
            self.current_flow = 'create_balance'
            self.out('Enter initial balance:')
            return
        if flow == 'create_balance':
            amount = self.parse_non_negative_amount(text)
            if amount is None:
                self.err('Invalid amount. Enter a non-negative number.')
                return
            ok, msg = self.system.process_create(self.flow_data['name'], amount)
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow in {'delete_name', 'disable_name', 'changeplan_name'}:
            self.flow_data['name'] = text
            self.current_flow = flow.replace('_name', '_account')
            self.out('Enter account number:')
            return

        if flow == 'delete_account':
            ok, msg = self.system.process_delete(self.flow_data['name'], text)
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow == 'disable_account':
            ok, msg = self.system.process_disable(self.flow_data['name'], text)
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None
            return

        if flow == 'changeplan_account':
            ok, msg = self.system.process_changeplan(self.flow_data['name'], text)
            self.out(msg) if ok else self.err(msg)
            self.current_flow = None

    @staticmethod
    def parse_positive_amount(text: str) -> float | None:
        """Parse a positive amount; return None when parsing fails or value is invalid."""
        try:
            amount = float(text)
        except ValueError:
            return None
        return amount if amount > 0 else None

    @staticmethod
    def parse_non_negative_amount(text: str) -> float | None:
        """Parse a non-negative amount; return None when parsing fails or value is invalid."""
        try:
            amount = float(text)
        except ValueError:
            return None
        return amount if amount >= 0 else None

    def write_transaction_file(self) -> None:
        """Write the daily Bank Account Transaction file to disk."""
        content = self.system.generate_transaction_file()
        filename = f"transaction_file_{datetime.now().strftime('%Y-%m-%d')}.txt"
        FileHandler.write_file(content, filename)
        self.out(f'Transaction file written: {filename}')


def main() -> None:
    """Program entry point."""
    app = BankingConsole()
    app.run()


if __name__ == '__main__':
    main()
