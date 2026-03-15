"""Transaction model and parser helpers for Front End and Back End files."""


class Transaction:
    """Represent one transaction record from a session or merged batch file."""

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

    def __init__(
        self,
        code: str,
        account_holder_name: str,
        account_number: str,
        amount: float = 0.0,
        misc: str = '  ',
        target_account: str | None = None,
    ) -> None:
        """Initialize a transaction with its shared fixed-width file fields."""
        self.code = code
        self.account_holder_name = account_holder_name
        self.account_number = str(account_number).zfill(5)
        self.amount = float(amount)
        self.misc = misc
        self.target_account = str(target_account).zfill(5) if target_account else None

    def to_file_string(self) -> str:
        """Format one fixed-width transaction line for the output file."""
        name = self.account_holder_name.ljust(20)[:20]
        account_num = self.account_number.zfill(5)
        amount = f"{self.amount:08.2f}"
        if self.code == self.CODES['TRANSFER']:
            target = (self.target_account or '').zfill(5)
            return f"{self.code} {name} {account_num} {amount}{target}"
        misc = self.misc.ljust(2)[:2]
        return f"{self.code} {name} {account_num} {amount}{misc}"

    @classmethod
    def from_file_string(cls, line: str) -> 'Transaction':
        """Parse one transaction line from a merged bank account transaction file."""
        clean_line = line.rstrip('\n')
        if len(clean_line) < 40:
            raise ValueError(f'Invalid transaction length ({len(clean_line)}). Expected at least 40.')

        code = clean_line[0:2]
        name = clean_line[3:23].rstrip()
        account_number = clean_line[24:29]
        amount_text = clean_line[30:38]

        try:
            amount = float(amount_text)
        except ValueError as exc:
            raise ValueError(f'Invalid transaction amount "{amount_text}".') from exc

        if code == cls.CODES['TRANSFER']:
            if len(clean_line) < 43:
                raise ValueError('Transfer transaction is missing the full destination account number.')
            return cls(code, name, account_number, amount, misc=clean_line[38:43], target_account=clean_line[38:43])

        misc = clean_line[38:40]
        return cls(code, name, account_number, amount, misc=misc)

    @classmethod
    def create_withdrawal(cls, account_holder_name: str, account_number: str, amount: float) -> 'Transaction':
        """Create a withdrawal transaction record."""
        return cls(cls.CODES['WITHDRAWAL'], account_holder_name, account_number, amount, '  ')

    @classmethod
    def create_transfer(cls, account_holder_name: str, from_account: str, to_account: str, amount: float) -> 'Transaction':
        """Create a transfer transaction record with the full destination account number."""
        return cls(
            cls.CODES['TRANSFER'],
            account_holder_name,
            from_account,
            amount,
            misc=str(to_account).zfill(5),
            target_account=to_account,
        )

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
