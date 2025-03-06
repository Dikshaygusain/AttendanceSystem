# initialize_database.py

import sqlite3


def initialize_database():
    conn = sqlite3.connect("attendance.db")

    # Create STUDENTS table for student details
    conn.execute("""
        CREATE TABLE IF NOT EXISTS STUDENTS (
            Id INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Age INTEGER
        )
    """)

    # Create Attendance table for logging attendance
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            Id INTEGER,
            Name TEXT,
            Date TEXT,
            Time TEXT,
            Status TEXT,
            PRIMARY KEY (Id, Date, Time)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()
