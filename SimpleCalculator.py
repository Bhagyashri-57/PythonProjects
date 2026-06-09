def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

def div(a, b):
    if b == 0:
        return "Cannot divide by zero"
    return a / b

print("Simple Calculator")
print("1. Add  2. Sub  3. Mul  4. Div")

choice = input("Enter choice: ")

a = float(input("Enter first number: "))
b = float(input("Enter second number: "))

if choice == "1":
    print("Result:", add(a, b))
elif choice == "2":
    print("Result:", sub(a, b))
elif choice == "3":
    print("Result:", mul(a, b))
elif choice == "4":
    print("Result:", div(a, b))
else:
    print("Invalid choice")
