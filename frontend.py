import sqlite3
import subprocess
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from datetime import datetime

# SQLite Database setup
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()


# Function to create the database table (if not already created)
def create_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS STUDENTS (
            Id TEXT PRIMARY KEY,
            Name TEXT,
            Age TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ATTENDANCE (
            Id TEXT,
            Date TEXT,
            FOREIGN KEY(Id) REFERENCES STUDENTS(Id)
        )
    ''')
    conn.commit()


# Function to add new member
def add_member():
    user_id = entry_id.get()
    name = entry_name.get()
    age = entry_age.get()

    if not user_id or not name or not age:
        messagebox.showerror("Input Error", "Please fill all fields.")
        return

    try:
        # Check if the user already exists
        cursor.execute("SELECT * FROM STUDENTS WHERE Id = ?", (user_id,))
        if cursor.fetchone():
            messagebox.showerror("Duplicate ID", f"Error: ID {user_id} already exists. Please use a unique ID.")
        else:
            # Insert the new member into the database
            cursor.execute("INSERT INTO STUDENTS (Id, Name, Age) VALUES (?, ?, ?)", (user_id, name, age))
            conn.commit()

            # Save the image to the 'Training_images' folder
            if image_path:
                img = Image.open(image_path)
                img.save(f"Training_images/{user_id}.jpg")  # Save the image with the user ID as filename
            messagebox.showinfo("Success", f"Member {name} added successfully.")
    except Exception as e:
        messagebox.showerror("Database Error", f"Error: {str(e)}")


# Function to choose the image file
def choose_image():
    global image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if image_path:
        image_preview = Image.open(image_path)
        image_preview = image_preview.resize((100, 100))  # Resize the image to fit in the preview
        image_preview = ImageTk.PhotoImage(image_preview)

        # Show the selected image in the preview
        image_label.config(image=image_preview)
        image_label.image = image_preview


# Function to delete today's attendance data from the database
def delete_today_attendance():
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date
    cursor.execute("DELETE FROM ATTENDANCE WHERE Date = ?", (today_date,))  # Delete all records for today
    conn.commit()  # Commit changes to the database
    print(f"Today's attendance has been deleted.")


# Function to handle Delete Today's Attendance in GUI
def delete_attendance():
    try:
        delete_today_attendance()  # Call the function to delete today's attendance
        messagebox.showinfo("Success", "Today's attendance has been successfully deleted.")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")


# Function to open the Add New Member window
def open_add_member_window():
    add_member_window = Toplevel(window)
    add_member_window.title("Add New Member")
    add_member_window.geometry("400x400")

    # ID field
    Label(add_member_window, text="Enter Student ID:").grid(row=0, column=0, padx=10, pady=5, sticky=E)
    entry_id = Entry(add_member_window)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    # Name field
    Label(add_member_window, text="Enter Student Name:").grid(row=1, column=0, padx=10, pady=5, sticky=E)
    entry_name = Entry(add_member_window)
    entry_name.grid(row=1, column=1, padx=10, pady=5)

    # Age field
    Label(add_member_window, text="Enter Student Age:").grid(row=2, column=0, padx=10, pady=5, sticky=E)
    entry_age = Entry(add_member_window)
    entry_age.grid(row=2, column=1, padx=10, pady=5)

    # Image preview area
    Label(add_member_window, text="Select Student Image:").grid(row=3, column=0, padx=10, pady=5, sticky=E)
    image_label = Label(add_member_window)
    image_label.grid(row=3, column=1, padx=10, pady=5)

    # Choose Image button
    choose_image_button = Button(add_member_window, text="Choose Image", command=choose_image)
    choose_image_button.grid(row=3, column=2, padx=10, pady=5)

    # Add Member button
    add_member_button = Button(add_member_window, text="Add Member", command=lambda: add_member())
    add_member_button.grid(row=4, column=1, padx=10, pady=10)

    add_member_window.mainloop()


# Set up the Tkinter window for the main menu
def create_main_window():
    global window
    window = Tk()
    window.title("ATTENDANCE SYSTEM")
    window.geometry("600x600")
    window.configure(bg="#f0f0f0")

    # Title Heading
    title_label = Label(window, text="ATTENDANCE SYSTEM", font=("Arial", 24, "bold"), bg="#4CAF50", fg="white",
                        width=30, height=2)
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    # Create the grid with 4 options
    options = [
        ("Add New User", open_add_member_window),
        ("Show Today's Attendance", show_attendance),
        ("Delete Today's Attendance", delete_attendance),
        ("Take Attendance", execute_face_recognition)
    ]

    for i, (text, command) in enumerate(options):
        row, col = divmod(i, 2)
        btn = Button(window, text=text, font=("Arial", 14), width=20, height=6, bg="lightblue", command=command)
        btn.grid(row=row + 1, column=col, padx=10, pady=10)

    window.mainloop()


# Placeholder functions for Show, Delete, and Take Attendance
def show_attendance():
    try:
        # Get today's date
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Connect to the database
        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()

        # Query the attendance for today
        cursor.execute("SELECT Name, Status FROM ATTENDANCE WHERE Date = ?", (today_date,))
        attendance_records = cursor.fetchall()

        # Check if there are no records for today
        if not attendance_records:
            messagebox.showinfo("No Attendance", "No attendance records found for today.")
            return

        # Create a new window to display today's attendance
        attendance_window = Toplevel()
        attendance_window.title("Today's Attendance")
        attendance_window.config(bg="#F0F8FF")

        # Header Label
        header_label = Label(attendance_window, text=f"Today's Attendance ({today_date})", font=("Helvetica", 16), bg="#F0F8FF", fg="blue")
        header_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Column headers
        name_label = Label(attendance_window, text="Name", font=("Helvetica", 12), bg="#F0F8FF", fg="green")
        name_label.grid(row=1, column=0, padx=10, pady=5)
        status_label = Label(attendance_window, text="Status", font=("Helvetica", 12), bg="#F0F8FF", fg="green")
        status_label.grid(row=1, column=1, padx=10, pady=5)

        # Display the attendance records
        row = 2
        for name, status in attendance_records:
            # Alternate row colors for better readability
            bg_color = "#D3D3D3" if row % 2 == 0 else "#F5F5F5"

            name_display = Label(attendance_window, text=name, font=("Helvetica", 12), bg=bg_color)
            name_display.grid(row=row, column=0, padx=10, pady=5)
            status_display = Label(attendance_window, text=status, font=("Helvetica", 12), bg=bg_color)
            status_display.grid(row=row, column=1, padx=10, pady=5)

            row += 1

        # Run the attendance window
        attendance_window.mainloop()

        # Close the database connection
        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", f"Error: {str(e)}")

def execute_face_recognition():
    try:
        # Run the face recognition script as a subprocess
        subprocess.run(['python', 'face_recognition_attendance.py'], check=True)

        # After executing, show today's attendance
        show_attendance()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Run the main application
if __name__ == "__main__":
    create_table()  # Create the tables if they don't exist
    create_main_window()
