import json
from pathlib import Path
from datetime import datetime
DATA_FILE = Path("bank_data.json")
MIN_BALANCE = 100.0
INTEREST_RATE = 4.0
def line():
    print("-" * 58)
def pause():
    input("\nPress Enter to continue...")
def non_empty(message):
    while True:
        value = input(message).strip()
        if value:
            return value
        print("This field cannot be empty.")
def amount_input(message):
    while True:
        try:
            amount = float(input(message))
            if amount > 0:
                return round(amount, 2)
            print("Amount must be greater than zero.")
        except ValueError:
            print("Enter a valid number.")
def account_number_input():
    while True:
        number = input("Enter account number: ").strip()
        if number.isdigit() and len(number) >= 4:
            return number
        print("Account number must contain at least 4 digits.")
def pin_input():
    while True:
        pin = input("Enter 4-digit PIN: ").strip()
        if pin.isdigit() and len(pin) == 4:
            return pin
        print("PIN must contain exactly 4 digits.")
def now():
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
def money(value):
    return f"Rs. {value:.2f}"
def empty_database():
    return {"accounts": {}, "next_account": 1001}
def load_database():
    if not DATA_FILE.exists():
        return empty_database()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if "accounts" not in data:
            data["accounts"] = {}
        if "next_account" not in data:
            data["next_account"] = 1001
        return data
    except (OSError, json.JSONDecodeError):
        print("Could not read saved data. Starting a new database.")
        return empty_database()
def save_database(data):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError:
        print("Could not save data.")
        return False
def add_transaction(account, kind, amount, note):
    account["transactions"].append({
        "date": now(),
        "type": kind,
        "amount": round(amount, 2),
        "note": note,
        "balance_after": round(account["balance"], 2)
    })
def get_account(data, number):
    return data["accounts"].get(number)
def create_account_data(data, name, age, phone, email, address, pin):
    number = str(data["next_account"])
    data["next_account"] += 1
    data["accounts"][number] = {
        "name": name,
        "age": age,
        "phone": phone,
        "email": email,
        "address": address,
        "pin": pin,
        "balance": 0.0,
        "status": "Active",
        "created_on": now(),
        "transactions": []
    }
    return number
def create_account(data):
    print("\n========== CREATE ACCOUNT ==========")
    name = non_empty("Enter full name: ")
    while True:
        age_text = input("Enter age: ").strip()
        if age_text.isdigit() and 18 <= int(age_text) <= 100:
            age = int(age_text)
            break
        print("Age must be between 18 and 100.")
    while True:
        phone = input("Enter 10-digit mobile number: ").strip()
        if phone.isdigit() and len(phone) == 10:
            break
        print("Enter a valid 10-digit mobile number.")
    while True:
        email = input("Enter email: ").strip()
        if "@" in email and "." in email:
            break
        print("Enter a valid email.")
    address = non_empty("Enter address: ")
    pin = pin_input()
    number = create_account_data(
        data, name, age, phone, email, address, pin
    )
    save_database(data)
    print("\nAccount created successfully.")
    print("Your account number is:", number)
    print("Remember your account number and PIN.")
    pause()
def login(data):
    print("\n========== ACCOUNT LOGIN ==========")
    number = account_number_input()
    account = get_account(data, number)
    if account is None:
        print("Account not found.")
        return None
    if account["status"] != "Active":
        print("This account is not active.")
        return None
    pin = pin_input()
    if pin != account["pin"]:
        print("Incorrect PIN.")
        return None
    print("Welcome,", account["name"])
    return number
def show_details(number, account):
    print("\n========== ACCOUNT DETAILS ==========")
    print("Account Number :", number)
    print("Name           :", account["name"])
    print("Age            :", account["age"])
    print("Phone          :", account["phone"])
    print("Email          :", account["email"])
    print("Address        :", account["address"])
    print("Balance        :", money(account["balance"]))
    print("Status         :", account["status"])
    print("Created On     :", account["created_on"])
    line()
def check_balance(data):
    number = login(data)
    if number is None:
        pause()
        return
    account = data["accounts"][number]
    print("Current balance:", money(account["balance"]))
    pause()
def deposit(data, number=None):
    if number is None:
        number = login(data)
    if number is None:
        pause()
        return
    account = data["accounts"][number]
    print("\n========== DEPOSIT ==========")
    amount = amount_input("Enter deposit amount: ")
    account["balance"] += amount
    add_transaction(account, "Deposit", amount, "Money deposited")
    save_database(data)
    print("Deposit successful.")
    print("New balance:", money(account["balance"]))
    pause()
def withdraw(data, number=None):
    if number is None:
        number = login(data)
    if number is None:
        pause()
        return
    account = data["accounts"][number]
    print("\n========== WITHDRAW ==========")
    print("Available:", money(account["balance"]))
    amount = amount_input("Enter withdrawal amount: ")
    if account["balance"] - amount < MIN_BALANCE:
        print("You must keep at least", money(MIN_BALANCE))
        pause()
        return
    account["balance"] -= amount
    add_transaction(account, "Withdrawal", amount, "Money withdrawn")
    save_database(data)
    print("Withdrawal successful.")
    print("New balance:", money(account["balance"]))
    pause()
def transfer(data, number=None):
    if number is None:
        number = login(data)
    if number is None:
        pause()
        return
    sender = data["accounts"][number]
    print("\n========== MONEY TRANSFER ==========")
    receiver_number = account_number_input()
    if receiver_number == number:
        print("You cannot transfer to the same account.")
        pause()
        return
    receiver = get_account(data, receiver_number)
    if receiver is None or receiver["status"] != "Active":
        print("Receiver account not found or inactive.")
        pause()
        return
    print("Receiver:", receiver["name"])
    amount = amount_input("Enter amount to transfer: ")
    if sender["balance"] - amount < MIN_BALANCE:
        print("Insufficient available balance.")
        pause()
        return
    sender["balance"] -= amount
    receiver["balance"] += amount
    add_transaction(
        sender, "Transfer Sent", amount,
        f"Sent to {receiver_number}"
    )
    add_transaction(
        receiver, "Transfer Received", amount,
        f"Received from {number}"
    )
    save_database(data)
    print("Transfer successful.")
    print("New balance:", money(sender["balance"]))
    pause()
def transactions(data, number=None):
    if number is None:
        number = login(data)
    if number is None:
        pause()
        return
    account = data["accounts"][number]
    print("\n========== TRANSACTION HISTORY ==========")
    records = account["transactions"]
    if not records:
        print("No transactions found.")
        pause()
        return
    for index, item in enumerate(records, 1):
        print("\nTransaction", index)
        print("Date          :", item["date"])
        print("Type          :", item["type"])
        print("Amount        :", money(item["amount"]))
        print("Note          :", item["note"])
        print("Balance After :", money(item["balance_after"]))
        line()
    pause()
def change_name(account):
    account["name"] = non_empty("Enter new name: ")
    print("Name updated.")
def change_phone(account):
    while True:
        value = input("Enter new 10-digit phone: ").strip()
        if value.isdigit() and len(value) == 10:
            account["phone"] = value
            print("Phone updated.")
            return
        print("Invalid phone number.")
def change_email(account):
    while True:
        value = input("Enter new email: ").strip()
        if "@" in value and "." in value:
            account["email"] = value
            print("Email updated.")
            return
        print("Invalid email.")
def change_address(account):
    account["address"] = non_empty("Enter new address: ")
    print("Address updated.")
def change_pin(account):
    new_pin = pin_input()
    if new_pin == account["pin"]:
        print("New PIN must be different.")
        return
    account["pin"] = new_pin
    print("PIN changed.")
def update_profile(data, number):
    account = data["accounts"][number]
    while True:
        print("\n========== UPDATE PROFILE ==========")
        print("1. Change Name")
        print("2. Change Phone")
        print("3. Change Email")
        print("4. Change Address")
        print("5. Change PIN")
        print("6. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            change_name(account)
        elif choice == "2":
            change_phone(account)
        elif choice == "3":
            change_email(account)
        elif choice == "4":
            change_address(account)
        elif choice == "5":
            change_pin(account)
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
            continue
        save_database(data)
def close_account(data, number=None):
    if number is None:
        number = login(data)
    if number is None:
        pause()
        return False
    account = data["accounts"][number]
    print("\n========== CLOSE ACCOUNT ==========")
    print("Current balance:", money(account["balance"]))
    if account["balance"] != 0:
        print("Balance must be zero before closing the account.")
        pause()
        return False
    confirm = input("Type CLOSE to confirm: ").strip().upper()
    if confirm != "CLOSE":
        print("Cancellation complete.")
        pause()
        return False
    account["status"] = "Closed"
    add_transaction(account, "Account Closed", 0, "Account closed")
    save_database(data)
    print("Account closed successfully.")
    pause()
    return True
def search_account(data):
    print("\n========== SEARCH ACCOUNT ==========")
    print("1. Search by account number")
    print("2. Search by name")
    choice = input("Enter choice: ").strip()
    if choice == "1":
        number = account_number_input()
        account = get_account(data, number)
        if account is None:
            print("Account not found.")
        else:
            show_details(number, account)
    elif choice == "2":
        keyword = non_empty("Enter name to search: ").lower()
        found = False
        for number, account in data["accounts"].items():
            if keyword in account["name"].lower():
                found = True
                print("\nAccount:", number)
                print("Name   :", account["name"])
                print("Status :", account["status"])
                print("Balance:", money(account["balance"]))
                line()
        if not found:
            print("No matching account found.")
    else:
        print("Invalid choice.")
    pause()
def admin_login():
    print("\n========== ADMIN LOGIN ==========")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return username == "admin" and password == "admin123"
def all_accounts(data):
    print("\n========== ALL ACCOUNTS ==========")
    if not data["accounts"]:
        print("No accounts available.")
        pause()
        return
    for number, account in data["accounts"].items():
        print("\nAccount:", number)
        print("Name   :", account["name"])
        print("Phone  :", account["phone"])
        print("Status :", account["status"])
        print("Balance:", money(account["balance"]))
        line()
    pause()
def statistics(data):
    active = 0
    closed = 0
    total = 0.0
    for account in data["accounts"].values():
        if account["status"] == "Active":
            active += 1
            total += account["balance"]
        else:
            closed += 1
    print("\n========== BANK STATISTICS ==========")
    print("Total accounts :", len(data["accounts"]))
    print("Active accounts:", active)
    print("Closed accounts:", closed)
    print("Total balance  :", money(total))
    if active:
        print("Average balance:", money(total / active))
    else:
        print("Average balance: Rs. 0.00")
    pause()
def admin_menu(data):
    if not admin_login():
        print("Invalid admin login.")
        pause()
        return
    while True:
        print("\n========== ADMIN PANEL ==========")
        print("1. View All Accounts")
        print("2. Search Account")
        print("3. Bank Statistics")
        print("4. Back")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            all_accounts(data)
        elif choice == "2":
            search_account(data)
        elif choice == "3":
            statistics(data)
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
def customer_menu(data, number):
    account = data["accounts"][number]
    while True:
        print("\n========== CUSTOMER MENU ==========")
        print("Welcome,", account["name"])
        print("1. Account Details")
        print("2. Check Balance")
        print("3. Deposit Money")
        print("4. Withdraw Money")
        print("5. Transfer Money")
        print("6. Transaction History")
        print("7. Mini Statement")
        print("8. Update Profile")
        print("9. Close Account")
        print("10. Logout")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            show_details(number, account)
            pause()
        elif choice == "2":
            print("Balance:", money(account["balance"]))
            pause()
        elif choice == "3":
            deposit(data, number)
        elif choice == "4":
            withdraw(data, number)
        elif choice == "5":
            transfer(data, number)
        elif choice == "6":
            transactions(data, number)
        elif choice == "7":
            mini_statement(data, number)
        elif choice == "8":
            update_profile(data, number)
        elif choice == "9":
            if close_account(data, number):
                break
        elif choice == "10":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")
def welcome():
    print("\n" + "*" * 58)
    print("*" + " BANK MANAGEMENT SYSTEM ".center(58) + "*")
    print("*" + " Python College Project ".center(58) + "*")
    print("*" * 58)
def main_menu(data):
    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Create New Account")
        print("2. Customer Login")
        print("3. Check Balance")
        print("4. Search Account")
        print("5. Admin Panel")
        print("6. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            create_account(data)
        elif choice == "2":
            number = login(data)
            if number is not None:
                customer_menu(data, number)
        elif choice == "3":
            check_balance(data)
        elif choice == "4":
            search_account(data)
        elif choice == "5":
            admin_menu(data)
        elif choice == "6":
            print("Thank you for using the system.")
            break
        else:
            print("Invalid choice. Select 1 to 6.")
def main():
    data = load_database()
    welcome()
    print("Simple console banking application")
    print("Data is saved locally in JSON format.")
    main_menu(data)
if __name__ == "__main__":
    main()
