import json
import os
from abc import ABC, abstractmethod
from datetime import datetime


DATA_FILE = "bank_data.json"


class BankAccount(ABC):
    """Base class for bank accounts."""

    def __init__(self, account_number, account_holder, balance=0.0):
        self._account_number = account_number
        self._account_holder = account_holder
        self._balance = float(balance)
        self._transactions = []

    @property
    def account_number(self):
        return self._account_number

    @property
    def account_holder(self):
        return self._account_holder

    @property
    def balance(self):
        return self._balance

    @abstractmethod
    def account_type(self):
        """Return the type of account."""
        pass

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self._balance += amount
        self._add_transaction("Deposit", amount)
        return self._balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if amount > self._balance:
            raise ValueError("Insufficient balance.")

        self._balance -= amount
        self._add_transaction("Withdrawal", amount)
        return self._balance

    def _add_transaction(self, transaction_type, amount):
        self._transactions.append({
            "type": transaction_type,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def get_transactions(self):
        return self._transactions.copy()

    def to_dict(self):
        return {
            "account_number": self._account_number,
            "account_holder": self._account_holder,
            "balance": self._balance,
            "account_type": self.account_type(),
            "transactions": self._transactions
        }


class SavingsAccount(BankAccount):
    """Savings account with a minimum balance rule."""

    def account_type(self):
        return "Savings"

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if self.balance - amount < 500:
            raise ValueError("Savings account must keep at least Rs. 500.")

        return super().withdraw(amount)


class CurrentAccount(BankAccount):
    """Current account with no minimum balance rule."""

    def account_type(self):
        return "Current"


class BankingSystem:
    """Manages accounts and stores data in a JSON file."""

    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.accounts = {}
        self.load_data()

    def create_account(self, account_number, account_holder, account_type):
        if not account_number.strip() or not account_holder.strip():
            raise ValueError("Account number and holder name are required.")

        if account_number in self.accounts:
            raise ValueError("This account number already exists.")

        if account_type == "1":
            account = SavingsAccount(account_number, account_holder)
        elif account_type == "2":
            account = CurrentAccount(account_number, account_holder)
        else:
            raise ValueError("Please select a valid account type.")

        self.accounts[account_number] = account
        self.save_data()
        return account

    def find_account(self, account_number):
        account = self.accounts.get(account_number)
        if account is None:
            raise ValueError("Account not found.")
        return account

    def save_data(self):
        data = [account.to_dict() for account in self.accounts.values()]
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    def load_data(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r") as file:
                data = json.load(file)

            for item in data:
                if item["account_type"] == "Savings":
                    account = SavingsAccount(
                        item["account_number"],
                        item["account_holder"],
                        item["balance"]
                    )
                else:
                    account = CurrentAccount(
                        item["account_number"],
                        item["account_holder"],
                        item["balance"]
                    )

                account._transactions = item.get("transactions", [])
                self.accounts[account.account_number] = account

        except (json.JSONDecodeError, KeyError, OSError) as error:
            print("Could not load saved data:", error)

    def show_accounts(self):
        if not self.accounts:
            print("No accounts have been created yet.")
            return

        for account in self.accounts.values():
            print(
                f"Account: {account.account_number} | "
                f"Name: {account.account_holder} | "
                f"Type: {account.account_type()} | "
                f"Balance: Rs. {account.balance:.2f}"
            )


def show_transactions(account):
    transactions = account.get_transactions()

    if not transactions:
        print("No transactions found.")
        return

    print("\n--- Transaction History ---")
    for transaction in transactions:
        print(
            f"{transaction['date']} | {transaction['type']} | "
            f"Rs. {transaction['amount']:.2f}"
        )


def main():
    bank = BankingSystem()

    while True:
        print("\n====== PYTHON BANKING SYSTEM ======")
        print("1. Create Account")
        print("2. View All Accounts")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. Check Balance")
        print("6. View Transaction History")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                number = input("Enter account number: ").strip()
                name = input("Enter account holder name: ").strip()
                print("1. Savings Account")
                print("2. Current Account")
                account_type = input("Choose account type: ").strip()

                account = bank.create_account(number, name, account_type)
                print(f"{account.account_type()} account created successfully.")

            elif choice == "2":
                bank.show_accounts()

            elif choice in ("3", "4", "5", "6"):
                number = input("Enter account number: ").strip()
                account = bank.find_account(number)

                if choice == "3":
                    amount = float(input("Enter deposit amount: Rs. "))
                    account.deposit(amount)
                    bank.save_data()
                    print(f"Deposit successful. New balance: Rs. {account.balance:.2f}")

                elif choice == "4":
                    amount = float(input("Enter withdrawal amount: Rs. "))
                    account.withdraw(amount)
                    bank.save_data()
                    print(f"Withdrawal successful. New balance: Rs. {account.balance:.2f}")

                elif choice == "5":
                    print(f"Current balance: Rs. {account.balance:.2f}")

                elif choice == "6":
                    show_transactions(account)

            elif choice == "7":
                print("Thank you for using the Banking System!")
                break

            else:
                print("Invalid option. Please choose from 1 to 7.")

        except ValueError as error:
            print("Error:", error)
        except OSError as error:
            print("File error:", error)
        finally:
            print("")


if __name__ == "__main__":
    main()
