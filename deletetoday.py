import sqlite3
from datetime import datetime

# SQLite Database setup
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Function to delete today's attendance data from the database
def delete_today_attendance():
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date
    cursor.execute("DELETE FROM ATTENDANCE WHERE Date = ?", (today_date,))  # Delete all records for today
    conn.commit()  # Commit changes to the database
    print(f"Today's attendance has been deleted.")

# Call this function to delete today's attendance
delete_today_attendance()

# Close the database connection
conn.close()
