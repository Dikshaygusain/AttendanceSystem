import sqlite3
from tkinter import *
from PIL import Image, ImageTk  # Use Pillow for image handling


# Function to show all members from the database
def show_all_members():
    # Initialize Tkinter window
    window = Tk()
    window.title("All Members")

    # Connect to the database
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    # Query to get all members from the database
    cursor.execute("SELECT Id, Name FROM STUDENTS")
    members = cursor.fetchall()

    # Start displaying images in the window
    row = 0
    for member in members:
        user_id, name = member
        img_path = f"Training_images/{user_id}.jpg"  # Assuming images are named after user IDs

        try:
            img = Image.open(img_path)  # Open the image file
            img = img.resize((100, 100))  # Resize image to fit in the window
            img_tk = ImageTk.PhotoImage(img)  # Convert to Tkinter compatible format

            # Create a label to display the image
            img_label = Label(window, image=img_tk)
            img_label.image = img_tk  # Keep reference to avoid garbage collection
            img_label.grid(row=row, column=0)

            # Label to show the ID
            id_label = Label(window, text=str(user_id))
            id_label.grid(row=row, column=1)

            # Label to show the name
            name_label = Label(window, text=name)
            name_label.grid(row=row, column=2)

            row += 1  # Move to the next row for each member
        except Exception as e:
            print(f"Error loading image for {name}: {e}")
            # If image loading fails, show a placeholder
            img_label = Label(window, text="No Image")
            img_label.grid(row=row, column=0)

            id_label = Label(window, text=str(user_id))
            id_label.grid(row=row, column=1)

            name_label = Label(window, text=name)
            name_label.grid(row=row, column=2)
            row += 1

    conn.close()

    window.mainloop()


# To call the function
show_all_members()
