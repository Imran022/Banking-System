"""Transaction model and factory helpers for Front End output records."""


class Transaction:
    """Represents one transaction line for the daily transaction output file."""

    CODES = {
        'WITHDRAWAL': '01',
        'TRANSFER': '02',
        'PAYBILL': '03',
        'DEPOSIT': '04',
        'CREATE': '05',
        'DELETE': '06',
        'DISABLE': '07',
        'CHANGEPLAN': '08',
        'END_SESSION': '00',
    }

    def __init__(self, code: str, account_holder_name: str, account_number: str, amount: float = 0.0, misc: str = '  ') -> None:
        """Initialize a transaction with code, account fields, amount, and misc field."""
        self.code = code
        self.account_holder_name = account_holder_name
        self.account_number = str(account_number)
        self.amount = float(amount)
        self.misc = misc

    def to_file_string(self) -> str:
        """Format one fixed-width transaction line for the output file."""
        name = self.account_holder_name.ljust(20)[:20]
        account_num = self.account_number.zfill(5)
        amount = f"{self.amount:.2f}".zfill(8)
        misc = self.misc.ljust(2)[:2]
        return f"{self.code} {name} {account_num} {amount}{misc}"

    @classmethod
    def create_withdrawal(cls, account_holder_name: str, account_number: str, amount: float) -> 'Transaction':
        """Create a withdrawal transaction record."""
        return cls(cls.CODES['WITHDRAWAL'], account_holder_name, account_number, amount, '  ')

    @classmethod
    def create_transfer(cls, account_holder_name: str, from_account: str, to_account: str, amount: float) -> 'Transaction':
        """Create a transfer transaction record with destination-account misc field."""
        to_padded = str(to_account).zfill(5)
        return cls(cls.CODES['TRANSFER'], account_holder_name, from_account, amount, to_padded[-2:])

    @classmethod
    def create_paybill(cls, account_holder_name: str, account_number: str, amount: float, company: str) -> 'Transaction':
        """Create a paybill transaction record."""
        return cls(cls.CODES['PAYBILL'], account_holder_name, account_number, amount, company)

    @classmethod
    def create_deposit(cls, account_holder_name: str, account_number: str, amount: float) -> 'Transaction':
        """Create a deposit transaction record."""
        return cls(cls.CODES['DEPOSIT'], account_holder_name, account_number, amount, '  ')

    @classmethod
    def create_account(cls, account_holder_name: str, account_number: str, initial_balance: float) -> 'Transaction':
        """Create an account-creation transaction record."""
        return cls(cls.CODES['CREATE'], account_holder_name, account_number, initial_balance, '  ')

    @classmethod
    def create_delete(cls, account_holder_name: str, account_number: str) -> 'Transaction':
        """Create an account-deletion transaction record."""
        return cls(cls.CODES['DELETE'], account_holder_name, account_number, 0, '  ')

    @classmethod
    def create_disable(cls, account_holder_name: str, account_number: str) -> 'Transaction':
        """Create an account-disable transaction record."""
        return cls(cls.CODES['DISABLE'], account_holder_name, account_number, 0, '  ')

    @classmethod
    def create_changeplan(cls, account_holder_name: str, account_number: str) -> 'Transaction':
        """Create a changeplan transaction record."""
        return cls(cls.CODES['CHANGEPLAN'], account_holder_name, account_number, 0, '  ')

    @classmethod
    def create_end_session(cls) -> 'Transaction':
        """Create the final end-of-session transaction record."""
        return cls(cls.CODES['END_SESSION'], ' ' * 20, '00000', 0, '  ')
