import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Function to get date input from the user
def get_date(prompt):
    while True:
        try:
            date = input(prompt)
            datetime.strptime(date, "%Y-%m-%d")  # Validate the format
            return date
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

# Connect to the 'Attendance' database (the one with both STUDENTS and ATTENDANCE)
conn = sqlite3.connect("Attendance.db")
cursor = conn.cursor()

# Ask for start and end dates dynamically
print("Enter the date range for attendance (YYYY-MM-DD format).")
start_date = get_date("Start date: ")
end_date = get_date("End date: ")

# Fetch unique users (ID and Name)
cursor.execute("""
    SELECT DISTINCT STUDENTS.ID, STUDENTS.Name 
    FROM STUDENTS 
    LEFT JOIN ATTENDANCE ON STUDENTS.ID = ATTENDANCE.ID
""")
users = cursor.fetchall()

# Generate the complete date range based on user input
date_range = []
current_date = datetime.strptime(start_date, "%Y-%m-%d")
end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
while current_date <= end_date_dt:
    date_range.append(current_date.strftime("%Y-%m-%d"))
    current_date += timedelta(days=1)

# Create a DataFrame structure
data = []
for user_id, name in users:
    row = [name, user_id]
    present_count = 0
    for date in date_range:
        cursor.execute("SELECT * FROM ATTENDANCE WHERE ID = ? AND Date = ?", (user_id, date))
        record = cursor.fetchone()
        if record:
            row.append("Present")
            present_count += 1
        else:
            row.append("Absent")
    row.append(present_count)  # Append total present count
    data.append(row)

# Create DataFrame and add a column for the total present count
header = ["Name", "ID"] + date_range + ["Total Present"]
df = pd.DataFrame(data, columns=header)

# Export to Excel
output_file = f"Attendance_{start_date}_to_{end_date}.xlsx"
df.to_excel(output_file, index=False)
print(f"Attendance exported to '{output_file}'.")

# Close connection
conn.close()
