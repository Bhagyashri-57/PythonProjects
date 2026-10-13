
import json
import os

FILE_NAME = "expenses.json"


def load_expenses():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    return []


def save_expenses(expenses):
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)


def add_expense(expenses):
    name = input("Enter expense name: ")

    try:
        amount = float(input("Enter amount (Rs.): "))
        if amount <= 0:
            print("Amount must be greater than zero!")
            return
    except ValueError:
        print("Please enter a valid amount!")
        return

    category = input("Enter category (Food/Travel/Other): ")

    expenses.append({
        "name": name,
        "amount": amount,
        "category": category
    })

    save_expenses(expenses)
    print("Expense added successfully!")


def view_expenses(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return

    total = 0
    print("\n------ YOUR EXPENSES ------")

    for expense in expenses:
        print(
            f"{expense['name']} - "
            f"Rs. {expense['amount']:.2f} - "
            f"{expense['category']}"
        )
        total += expense["amount"]

    print(f"\nTotal spending: Rs. {total:.2f}")


def main():
    expenses = load_expenses()

    while True:
        print("\n===== SMART EXPENSE TRACKER =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            print("Thank you for using the tracker!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
