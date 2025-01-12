import re
import json
from typing import List, Dict, Union
from datetime import datetime


class LedgerParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def __str__(self):
        return f"LedgerParser(file_path='{self.file_path}')"

    def parse(self) -> List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]:
        transactions = []

        with open(self.file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        current_transaction = None

        for line in lines:
            line = line.strip()
            if not line:
                # Save the current transaction and reset
                if current_transaction:
                    transactions.append(current_transaction)
                    current_transaction = None
                continue

            date_match = re.match(
                r"^(\d{4}/\d{2}/\d{2})(?: (\d{2}:\d{2}:\d{2}))?( \*?)?(.*)$", line
            )
            if date_match:
                # Parse transaction header
                date, time, verified, description = date_match.groups()
                current_transaction = {
                    "date": date,
                    "time": time if time else None,
                    "verified": bool(verified and verified.strip() == "*"),
                    "description": description.strip(),
                    "accounts": [],
                }
            elif current_transaction:
                # Parse account line
                account_match = re.match(
                    r"^([A-Za-z0-9:]+)\s+([A-Z]{3})\s+(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)$",
                    line,
                )
                if not account_match:
                    account_match = re.match(
                        r"^([A-Za-z0-9: ]+)\s+([A-Z]{3})\s+(-?\d+(?:\.\d+)?)$", line
                    )

                if account_match:
                    account_name, unit, amount = account_match.groups()
                    current_transaction["accounts"].append(
                        {
                            "account": account_name.replace(" ", ""),
                            "unit": unit,
                            "amount": float(amount.replace(",", "")),
                        }
                    )

        # Add the last transaction if any
        if current_transaction:
            transactions.append(current_transaction)

        return transactions

    def to_json(self) -> str:
        transactions = self.parse()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    def get_registers_between_dates(self, start_date: str, end_date: str) -> str:
        transactions = self.parse()
        start = datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.strptime(end_date, "%Y/%m/%d")

        filtered_transactions = [
            transaction
            for transaction in transactions
            if start <= datetime.strptime(transaction["date"], "%Y/%m/%d") <= end
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def get_registers_by_month(self, year: int, month: int) -> str:
        transactions = self.parse()
        filtered_transactions = [
            transaction
            for transaction in transactions
            if datetime.strptime(transaction["date"], "%Y/%m/%d").year == year
            and datetime.strptime(transaction["date"], "%Y/%m/%d").month == month
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def calculate_balances(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, float]]:
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name not in balances:
                    balances[account_name] = {}

                if unit not in balances[account_name]:
                    balances[account_name][unit] = 0.0

                balances[account_name][unit] += amount

        return balances

    def calculate_balance_for_account(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        target_account: str,
    ) -> Dict[str, float]:
        account_balance = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(target_account):
                    if unit not in account_balance:
                        account_balance[unit] = 0.0

                    account_balance[unit] += amount

        return account_balance

    def _create_transaction(
        self,
        date: str,
        description: str,
        accounts: List[Dict[str, Union[str, float]]],
        verify: bool = False,
    ) -> str:
        transaction = f"{date}{' * ' if verify else ' '}{description}\n"
        for account in accounts:
            account_line = f"    {account['account']}    {account['unit']} {account['amount']:.2f}"
            transaction += account_line + "\n"
        return transaction

    def add_transaction(
        self, date: str, description: str, accounts: List[Dict[str, Union[str, float]]]
    ):
        """
        Adds a new transaction to the ledger file.

        :param date: Date of the transaction in 'YYYY/MM/DD' format.
        :param description: Description of the transaction.
        :param accounts: List of account dictionaries with 'account', 'unit', and 'amount'.
        """
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write("\n")
            transaction_string = self._create_transaction(date, description, accounts)
            file.write(transaction_string)
            file.write("\n")


# Ejemplo de uso
if __name__ == "__main__":
    parser = LedgerParser("test.ledger")
    transactions_json = parser.parse()
    print(parser.get_registers_between_dates("2025/01/02", "2025/01/04"))
    print(parser.get_registers_by_month(2025, 1))
    balances = parser.calculate_balances(transactions_json)
    print(json.dumps(balances, indent=4, ensure_ascii=False))
    specific_balance = parser.calculate_balance_for_account(transactions_json, "Assets")
    print(json.dumps(specific_balance, indent=4, ensure_ascii=False))
