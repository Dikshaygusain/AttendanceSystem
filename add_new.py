import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import shutil

# Function to add new member
def add_member():
    user_id = entry_id.get()
    name = entry_name.get()
    age = entry_age.get()

    if not user_id or not name or not age:
        messagebox.showerror("Input Error", "Please fill all fields.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()

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
        conn.close()
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

# Set up the Tkinter window
window = Tk()
window.title("Add New Member")

# Global variable to hold the image path
image_path = ""

# ID field
Label(window, text="Enter Student ID:").grid(row=0, column=0, padx=10, pady=5, sticky=E)
entry_id = Entry(window)
entry_id.grid(row=0, column=1, padx=10, pady=5)

# Name field
Label(window, text="Enter Student Name:").grid(row=1, column=0, padx=10, pady=5, sticky=E)
entry_name = Entry(window)
entry_name.grid(row=1, column=1, padx=10, pady=5)

# Age field
Label(window, text="Enter Student Age:").grid(row=2, column=0, padx=10, pady=5, sticky=E)
entry_age = Entry(window)
entry_age.grid(row=2, column=1, padx=10, pady=5)

# Image preview area
Label(window, text="Select Student Image:").grid(row=3, column=0, padx=10, pady=5, sticky=E)
image_label = Label(window)
image_label.grid(row=3, column=1, padx=10, pady=5)

# Choose Image button
choose_image_button = Button(window, text="Choose Image", command=choose_image)
choose_image_button.grid(row=3, column=2, padx=10, pady=5)

# Add Member button
add_member_button = Button(window, text="Add Member", command=add_member)
add_member_button.grid(row=4, column=1, padx=10, pady=10)

# Run the GUI
window.mainloop()
