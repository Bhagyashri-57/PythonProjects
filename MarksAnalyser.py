
import csv
import os

SUBJECTS = ["English", "Kannada", "Maths", "Science", "Social"]
CSV_FILE = "student_results.csv"
PASS_MARK = 35


def calculate_result(marks):
    total = sum(marks)
    percentage = total / len(SUBJECTS)

    if any(mark < PASS_MARK for mark in marks):
        return total, percentage, "F", "Fail"

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "E"

    return total, percentage, grade, "Pass"


def load_students():
    students = []

    if not os.path.exists(CSV_FILE):
        return students

    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                marks = [int(row[sub]) for sub in SUBJECTS]
                total, percentage, grade, status = calculate_result(marks)

                students.append({
                    "roll": row["Roll Number"],
                    "name": row["Name"],
                    "marks": marks,
                    "total": total,
                    "percentage": percentage,
                    "grade": grade,
                    "status": status
                })
    except (OSError, KeyError, ValueError):
        print("Could not read the saved records.")
        return []

    return students


def save_students(students):
    fields = [
        "Roll Number", "Name", *SUBJECTS,
        "Total", "Percentage", "Grade", "Status"
    ]

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for s in students:
            row = {
                "Roll Number": s["roll"],
                "Name": s["name"],
                "Total": s["total"],
                "Percentage": f"{s['percentage']:.2f}",
                "Grade": s["grade"],
                "Status": s["status"]
            }

            for i, subject in enumerate(SUBJECTS):
                row[subject] = s["marks"][i]

            writer.writerow(row)


def add_student(students):
    print("\n--- Add Student ---")
    roll = input("Enter roll number: ").strip()
    name = input("Enter student name: ").strip()

    if not roll or not name:
        print("Name and roll number cannot be empty.")
        return

    if any(s["roll"].lower() == roll.lower() for s in students):
        print("This roll number already exists.")
        return

    marks = []

    for subject in SUBJECTS:
        while True:
            try:
                mark = int(input(f"Enter {subject} marks (0-100): "))

                if 0 <= mark <= 100:
                    marks.append(mark)
                    break

                print("Enter marks between 0 and 100.")

            except ValueError:
                print("Please enter a valid whole number.")

    total, percentage, grade, status = calculate_result(marks)

    student = {
        "roll": roll,
        "name": name,
        "marks": marks,
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "status": status
    }

    students.append(student)
    save_students(students)

    print("\nStudent added successfully!")
    print_result(student)


def print_result(s):
    print("\n========== STUDENT RESULT ==========")
    print("Roll Number:", s["roll"])
    print("Name:", s["name"])

    for i, subject in enumerate(SUBJECTS):
        print(f"{subject}: {s['marks'][i]}/100")

    print(f"Total: {s['total']}/500")
    print(f"Percentage: {s['percentage']:.2f}%")
    print("Grade:", s["grade"])
    print("Status:", s["status"])
    print("====================================")


def view_students(students):
    if not students:
        print("No student records found.")
        return

    print("\n--- All Student Results ---")
    print(f"{'Roll':<10}{'Name':<18}{'Total':<10}"
          f"{'Percent':<12}{'Grade':<8}{'Status'}")

    print("-" * 70)

    for s in students:
        print(
            f"{s['roll']:<10}"
            f"{s['name'][:17]:<18}"
            f"{s['total']:<10}"
            f"{s['percentage']:.2f}%{'':<6}"
            f"{s['grade']:<8}"
            f"{s['status']}"
        )


def find_topper(students):
    if not students:
        print("No student records found.")
        return

    highest = max(s["total"] for s in students)
    toppers = [s for s in students if s["total"] == highest]

    print("\n========== CLASS TOPPER ==========")

    for s in toppers:
        print("Name:", s["name"])
        print("Roll Number:", s["roll"])
        print(f"Total: {s['total']}/500")
        print(f"Percentage: {s['percentage']:.2f}%")

    if len(toppers) > 1:
        print("There is a tie between these students!")


def search_student(students):
    roll = input("Enter roll number to search: ").strip()

    for s in students:
        if s["roll"].lower() == roll.lower():
            print_result(s)
            return

    print("Student not found.")


def main():
    students = load_students()

    while True:
        print("\n===== STUDENT MARKS ANALYZER =====")
        print("1. Add Student")
        print("2. View All Results")
        print("3. Find Class Topper")
        print("4. Search Student")
        print("5. Export Results to CSV")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_student(students)

        elif choice == "2":
            view_students(students)

        elif choice == "3":
            find_topper(students)

        elif choice == "4":
            search_student(students)

        elif choice == "5":
            save_students(students)
            print("Results saved to", CSV_FILE)

        elif choice == "6":
            save_students(students)
            print("All results saved. Goodbye!")
            break

        else:
            print("Invalid choice. Enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
