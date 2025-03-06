import sqlite3


def add_student(Id, Name, Age):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Check if ID already exists
    cursor.execute("SELECT * FROM STUDENTS WHERE Id = ?", (Id,))
    existing_student = cursor.fetchone()
    if existing_student:
        print(f"Error: ID {Id} already exists. Please use a unique ID.")
    else:
        # Insert student record
        cursor.execute("INSERT INTO STUDENTS (Id, Name, Age) VALUES (?, ?, ?)", (Id, Name, Age))
        conn.commit()  # Commit after the insert operation
        print(f"Student '{Name}' with ID {Id} added successfully.")

    # Confirm the data inserted
    cursor.execute("SELECT * FROM STUDENTS")
    all_students = cursor.fetchall()
    print("Current students in the database:", all_students)

    conn.close()


def main():
    print("Add Students to the Database")
    while True:
        try:
            Id = int(input("Enter Student ID (integer): "))
            Name = input("Enter Student Name: ").strip()
            Age = int(input("Enter Student Age: "))
            add_student(Id, Name, Age)
        except ValueError:
            print("Invalid input. Please enter numeric values for ID and Age.")

        cont = input("Do you want to add another student? (y/n): ").strip().lower()
        if cont != 'y':
            break


if __name__ == "__main__":
    main()
