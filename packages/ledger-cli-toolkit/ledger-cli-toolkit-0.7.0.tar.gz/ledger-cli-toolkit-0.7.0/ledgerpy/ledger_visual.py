from tabulate import tabulate
from typing import List, Dict, Union


class LedgerVisual:
    def __init__(self):
        pass

    def display_journal_table(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        title_table="Ledger",
    ):
        """
        Display the transactions in a journal-like table format with columns:
        - N° (Transaction Index)
        - Date (Transaction Date and Time)
        - Concept (Account Name)
        - Debit (Positive Amounts)
        - Credit (Negative Amounts)

        At the end of the table, show "SUMAS IGUALES" with the total debit and credit.
        """
        table_data = []
        total_debit = 0.0
        total_credit = 0.0

        for idx, transaction in enumerate(transactions_json, start=1):
            for account in transaction["accounts"]:
                date_time = transaction["date"]
                if transaction.get("time"):
                    date_time += f" {transaction['time']}"

                account_name = account["account"]
                amount = account["amount"]
                debit = amount if amount > 0 else 0
                credit = -amount if amount < 0 else 0

                table_data.append([idx, date_time, account_name, debit, credit])

                total_debit += debit
                total_credit += credit

        # Add SUMAS IGUALES row
        table_data.append(["", "", "SUMAS IGUALES", total_debit, total_credit])

        headers = ["N°", "Fecha", "Concepto", "Debe", "Haber"]
        table = tabulate(
            table_data, headers=headers, floatfmt=".2f", tablefmt="outline"
        )
        output = f"{title_table}\n{'=' * len(title_table)}\n{table}"
        print(output)

    @staticmethod
    def display_general_balance(account_balances: Dict[str, Dict[str, float]]):
        table = []
        total_balance = 0.0

        for index, (account, balances) in enumerate(account_balances.items(), start=1):
            for unit, balance in balances.items():
                table.append([index, account, unit, f"{balance:.2f}"])
                total_balance += balance

        table.append(["", "BALANCE", "", f"{total_balance:.2f}"])
        print(
            tabulate(
                table, headers=["N°", "Concepto", "Unidad", "Saldo"], tablefmt="outline"
            )
        )


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de datos de transacciones
    example_transactions = [
        {
            "date": "2025/01/02",
            "time": "12:00:00",
            "verified": True,
            "description": "Compra de insumos",
            "accounts": [
                {"account": "Expenses:Office", "unit": "USD", "amount": 100.0},
                {"account": "Assets:Cash", "unit": "USD", "amount": -100.0},
            ],
        },
        {
            "date": "2025/01/03",
            "verified": True,
            "description": "Pago de servicios",
            "accounts": [
                {"account": "Expenses:Utilities", "unit": "USD", "amount": 50.0},
                {"account": "Assets:Bank", "unit": "USD", "amount": -50.0},
            ],
        },
    ]

    balances = {
        "Assets:Cash": {"MXN": 35.0},
        "Liabilities:Debts:Belem": {"MXN": -800.0},
        "Assets:Bank:Azteca:Guardadito": {"MXN": 0.0},
        "Assets:Bank:MercadoPago": {"MXN": 0.0},
        "Liabilities:CreditCard:MercadoPago": {"MXN": 78.36},
        "Assets:Bank:Nubank": {"MXN": -2.2737367544323206e-13},
        "Expenses:Pareja:Regalos": {"MXN": 270.0},
        "Income:Otros": {"MXN": -1250.0},
        "Income:Educacion": {"MXN": -500.0},
        "Expenses:Transporte": {"MXN": 65.0},
        "Expenses:Educacion:Universidad": {"MXN": 30.0},
        "Expenses:Pareja:Salidas": {"MXN": 373.0},
        "Expenses:Propinas": {"MXN": 36.0},
        "Assets:Bank:UALA": {"MXN": 1151.64},
        "Expenses:Otros": {"MXN": 81.0},
    }

    visual = LedgerVisual()
    visual.display_journal_table(example_transactions)
    visual.display_general_balance(balances)
