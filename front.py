import sqlite3
import pandas as pd
import subprocess
import streamlit as st
from PIL import Image
from datetime import datetime, timedelta


import requests
import jwt
import time

import sqlite3
import pandas as pd
import subprocess
import streamlit as st
from PIL import Image
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode


# Function to get OAuth access token
def get_oauth_access_token():
    client_id = "9jA60H3aRAa_JZoW4_TLpQ"  # Replace with your Client ID
    client_secret = "p9ogiyw48L9sxSTmEi6Luwvw5RJCbH8f"  # Replace with your Client Secret

    # Create the request body
    data = {
        "grant_type": "client_credentials",  # Use client_credentials for server-to-server auth
        "client_id": client_id,
        "client_secret": client_secret,
    }

    # Send POST request to get the token
    response = requests.post(
        "https://zoom.us/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=urlencode(data),
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]  # Access token from response
        return access_token
    else:
        st.error(f"Error fetching OAuth token: {response.text}")
        return None


# Function to create a Zoom meeting
def create_zoom_meeting(host_email, topic="Class Meeting", duration=30):
    # Get OAuth access token
    access_token = get_oauth_access_token()  # Get the OAuth access token

    if access_token is None:
        st.error("Failed to obtain OAuth access token")
        return

    # Zoom API endpoint
    url = f"https://api.zoom.us/v2/users/dikshaygusain9568@gmail.com/meetings"

    # Meeting data
    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": (datetime.now() + timedelta(minutes=5)).isoformat(),  # Start time in ISO format
        "duration": duration,  # Duration in minutes
        "settings": {
            "join_before_host": True,
            "mute_upon_entry": True,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",  # Use OAuth access token
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            meeting_data = response.json()
            meeting_link = meeting_data["join_url"]
            st.success(f"Meeting created successfully: {meeting_link}")
            return meeting_link
        else:
            st.error(f"Error creating meeting: {response.text}")
    except Exception as e:
        st.error(f"Failed to create meeting: {str(e)}")


# zoom









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
            Status TEXT,
            FOREIGN KEY(Id) REFERENCES STUDENTS(Id)
        )
    ''')
    conn.commit()


# Function to add a new member
def add_member(user_id, name, age, image_path):
    if not user_id or not name or not age:
        st.error("Please fill all fields.")
        return

    try:
        # Check if the user already exists
        cursor.execute("SELECT * FROM STUDENTS WHERE Id = ?", (user_id,))
        if cursor.fetchone():
            st.error(f"Error: ID {user_id} already exists. Please use a unique ID.")
        else:
            # Insert the new member into the database
            cursor.execute("INSERT INTO STUDENTS (Id, Name, Age) VALUES (?, ?, ?)", (user_id, name, age))
            conn.commit()

            # Save the image to the 'Training_images' folder
            if image_path:
                img = Image.open(image_path)
                img.save(f"Training_images/{user_id}.jpg")  # Save the image with the user ID as filename
            st.success(f"Member {name} added successfully.")
    except Exception as e:
        st.error(f"Database Error: {str(e)}")


# Function to delete today's attendance data from the database
def delete_today_attendance():
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date
    cursor.execute("DELETE FROM ATTENDANCE WHERE Date = ?", (today_date,))  # Delete all records for today
    conn.commit()  # Commit changes to the database
    st.success("Today's attendance has been deleted.")


# Function to show today's attendance
import pandas as pd

def show_attendance():
    try:
        # Get today's date
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Query the list of all students
        cursor.execute("SELECT Id, Name FROM STUDENTS")
        students = cursor.fetchall() # fetch whole row

        # If no students are in the database
        if not students:
            st.info("No students found in the database.")
            return

        # Create a list to store the attendance status
        attendance_records = []

        # For each student, check their attendance for today
        for student_id, student_name in students:
            cursor.execute("SELECT Status FROM ATTENDANCE WHERE Id = ? AND Date = ?", (student_id, today_date))
            record = cursor.fetchone() # retrieve 1st row

            # If the student has an attendance record for today, use that status
            if record:
                status = record[0]
            else:
                status = "Absent"  # If no attendance record, mark as absent

            # Add the student and their status to the list
            attendance_records.append({"Name": student_name, "Status": status})

        # Display the attendance records in a proper table format using pandas
        st.subheader(f"Today's Attendance ({today_date})")
        if attendance_records:
            df = pd.DataFrame(attendance_records)  # Create a DataFrame for structured display
            st.table(df)  # Display the table

    except Exception as e:
        st.error(f"Database Error: {str(e)}")



# Function to execute face recognition
def execute_face_recognition():
    try:
        # Run the face recognition script as a subprocess
        subprocess.run(['python', 'face_recognition_attendance.py'], check=True)
        # After executing, show today's attendance
        show_attendance()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Function to delete all attendance records
def delete_all_attendance():
    try:
        cursor.execute("DELETE FROM ATTENDANCE")
        conn.commit()
        st.success("All attendance records have been deleted.")
    except Exception as e:
        st.error(f"Error deleting attendance: {str(e)}")


# Function to show attendance from a date range and allow Excel download
import os
from PIL import Image
import io
import streamlit as st

def show_all_members():
    try:
        # Fetch all members from the database
        cursor.execute("SELECT Id, Name FROM STUDENTS")
        members = cursor.fetchall()

        if not members:
            st.info("No members found in the database.")
            return

        # Create a DataFrame to display members
        member_data = []
        for member in members:
            user_id, name = member
            img_path = f"Training_images/{user_id}.jpg"  # Image path

            if os.path.exists(img_path):  # Check if image exists
                try:
                    img = Image.open(img_path)  # Open the image
                    img = img.resize((100, 100))  # Resize image for display

                    # Convert image to bytes for Streamlit display
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()

                    member_data.append([name, user_id, img_byte_arr])
                except Exception as e:
                    # In case of an error loading the image, show a placeholder
                    member_data.append([name, user_id, None])
            else:
                # If image doesn't exist, add a placeholder
                member_data.append([name, user_id, None])

        # Display members in a table with images
        st.subheader("All Members in the Database")

        for data in member_data:
            name, user_id, img_data = data
            st.write(f"*Name:* {name} | *ID:* {user_id}")

            if img_data:
                st.image(img_data, caption=f"ID: {user_id}", width=100)
            else:
                st.write("*No Image Available*")

    except Exception as e:
        st.error(f"Error fetching member data: {str(e)}")


# Function to show attendance records from a date range and allow Excel download
def show_records():
    try:
        # Get start and end date inputs from the user
        start_date = st.date_input("Start Date", datetime.today())
        end_date = st.date_input("End Date", datetime.today())

        # Validate if end date is after start date
        if start_date > end_date:
            st.error("End Date cannot be before Start Date.")
            return

        # Fetch unique users (ID and Name)
        cursor.execute(""" 
            SELECT DISTINCT STUDENTS.ID, STUDENTS.Name 
            FROM STUDENTS 
            LEFT JOIN ATTENDANCE ON STUDENTS.ID = ATTENDANCE.ID
        """)
        users = cursor.fetchall()

        # Generate the complete date range based on user input
        date_range = pd.date_range(start_date, end_date).strftime('%Y-%m-%d').tolist()

        # Create a DataFrame structure to hold the attendance data
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
            row.append(present_count)  # Total present count for the user
            data.append(row)

        # Create a DataFrame and display it as a table
        header = ["Name", "ID"] + date_range + ["Total Present"]
        df = pd.DataFrame(data, columns=header)

        # Display the attendance table interactively
        st.subheader(f"Attendance from {start_date} to {end_date}")
        st.dataframe(df)  # This renders a proper interactive table

        # Export to Excel
        output_file = f"Attendance_{start_date}to{end_date}.xlsx"
        if st.button("Download Attendance as Excel"):
            df.to_excel(output_file, index=False)
            st.success(f"Attendance exported to '{output_file}'.")

        # Show all members option
        if st.button("Show All Members Data"):
            show_all_members()

    except Exception as e:
        st.error(f"Error displaying records: {str(e)}")



# Main Streamlit interface
def main():
    create_table()  # Create the tables if they don't exist

    st.title("Attendance System", anchor="center")

    # Display options using radio buttons for smoother navigation
    menu = ["Home", "Add New Member", "Show Today's Attendance", "Delete Today's Attendance", "Take Attendance",
            "Show Records", "Create Zoom Meeting"]  # Add Zoom option
    choice = st.sidebar.radio("Select an option", menu)

    # Create an empty container for dynamic content updates
    page_content = st.empty()

    # Home Page Section
    if choice == "Home":
        page_content.empty()  # Clear previous content
        st.markdown("""
        *About the App:*
        This application is designed to simplify the process of managing student attendance. 
        It allows you to:
        - Add new members (students) to the system.
        - Take attendance using face recognition.
        - View today's attendance records.
        - Delete today's attendance records if necessary.
        """)

    # Add New Member Section
    elif choice == "Add New Member":
        page_content.empty()  # Clear previous content
        st.subheader("Add New Member")
        user_id = st.text_input("Enter Student ID:")
        name = st.text_input("Enter Student Name:")
        age = st.text_input("Enter Student Age:")

        # Image upload
        image_path = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

        if image_path:
            img = Image.open(image_path)
            st.image(img, caption="Uploaded Image", use_column_width=True)

        if st.button("Add Member"):
            add_member(user_id, name, age, image_path)

    # Show Today's Attendance Section
    elif choice == "Show Today's Attendance":
        page_content.empty()  # Clear previous content
        show_attendance()

    # Delete Today's Attendance Section
    elif choice == "Delete Today's Attendance":
        page_content.empty()  # Clear previous content
        st.warning("Are you sure you want to delete today's attendance?")
        if st.button("Delete Today's Attendance"):
            delete_today_attendance()

    # Take Attendance Section
    elif choice == "Take Attendance":
        page_content.empty()  # Clear previous content
        st.subheader("Face Recognition Attendance")
        if st.button("Start Face Recognition"):
            execute_face_recognition()

    # Show Records Section
    elif choice == "Show Records":
        page_content.empty()  # Clear previous content
        st.subheader("Attendance Records")

        # Add the new option to the menu
        menu = ["Delete All Attendance", "Show Attendance from Date to Date", "Show All Members Data"]
        sub_choice = st.selectbox("Choose an option", menu)

        # Handle delete all attendance case
        if sub_choice == "Delete All Attendance":
            if st.button("Delete All Attendance"):
                delete_all_attendance()

        # Show attendance between specific dates
        elif sub_choice == "Show Attendance from Date to Date":
            show_records()

        # Show all student data (ID, Name, Image)
        elif sub_choice == "Show All Members Data":
            show_all_members()

    # Create Zoom Meeting Section (added)
    elif choice == "Create Zoom Meeting":
        page_content.empty()  # Clear previous content
        st.subheader("Create Zoom Meeting")
        host_email = st.text_input("Enter Host Email:")
        topic = st.text_input("Enter Meeting Topic:", "Class Meeting")
        duration = st.number_input("Enter Meeting Duration (in minutes):", min_value=1, value=30)

        if st.button("Create Meeting"):
            if host_email:
                meeting_link = create_zoom_meeting(host_email, topic, duration)
                if meeting_link:
                    st.success(f"Zoom Meeting Created! Join using this link: {meeting_link}")
            else:
                st.error("Please enter the host email.")

    # Footer with Creator Info (always at the bottom)
    st.markdown("<p style='text-align: center; font-size: 12px; margin-top: 40px;'>Made by Dikshay Gusain</p>",
                unsafe_allow_html=True)


# Run the main app
if __name__ == "__main__":
    main()


# Main Streamlit interface
# def main():
#     create_table()  # Create the tables if they don't exist
#
#     st.title("Attendance System", anchor="center")
#
#     # Display options using radio buttons for smoother navigation
#     menu = ["Home", "Add New Member", "Show Today's Attendance", "Delete Today's Attendance", "Take Attendance",
#             "Show Records"]
#     choice = st.sidebar.radio("Select an option", menu)
#
#     # Create an empty container for dynamic content updates
#     page_content = st.empty()
#
#     # Home Page Section
#     if choice == "Home":
#         page_content.empty()  # Clear previous content
#         st.markdown("""
#         *About the App:*
#         This application is designed to simplify the process of managing student attendance.
#         It allows you to:
#         - Add new members (students) to the system.
#         - Take attendance using face recognition.
#         - View today's attendance records.
#         - Delete today's attendance records if necessary.
#         """)
#
#     # Add New Member Section
#     elif choice == "Add New Member":
#         page_content.empty()  # Clear previous content
#         st.subheader("Add New Member")
#         user_id = st.text_input("Enter Student ID:")
#         name = st.text_input("Enter Student Name:")
#         age = st.text_input("Enter Student Age:")
#
#         # Image upload
#         image_path = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])
#
#         if image_path:
#             img = Image.open(image_path)
#             st.image(img, caption="Uploaded Image", use_column_width=True)
#
#         if st.button("Add Member"):
#             add_member(user_id, name, age, image_path)
#
#     # Show Today's Attendance Section
#     elif choice == "Show Today's Attendance":
#         page_content.empty()  # Clear previous content
#         show_attendance()
#
#     # Delete Today's Attendance Section
#     elif choice == "Delete Today's Attendance":
#         page_content.empty()  # Clear previous content
#         st.warning("Are you sure you want to delete today's attendance?")
#         if st.button("Delete Today's Attendance"):
#             delete_today_attendance()
#
#     # Take Attendance Section
#     elif choice == "Take Attendance":
#         page_content.empty()  # Clear previous content
#         st.subheader("Face Recognition Attendance")
#         if st.button("Start Face Recognition"):
#             execute_face_recognition()
#
#     # Show Records Section
#     elif choice == "Show Records":
#         page_content.empty()  # Clear previous content
#         st.subheader("Attendance Records")
#
#         # Add the new option to the menu
#         menu = ["Delete All Attendance", "Show Attendance from Date to Date", "Show All Members Data"]
#         sub_choice = st.selectbox("Choose an option", menu)
#
#         # Handle delete all attendance case
#         if sub_choice == "Delete All Attendance":
#             if st.button("Delete All Attendance"):
#                 delete_all_attendance()
#
#         # Show attendance between specific dates
#         elif sub_choice == "Show Attendance from Date to Date":
#             show_records()
#
#         # Show all student data (ID, Name, Image)
#         elif sub_choice == "Show All Members Data":
#             show_all_members()
#
#     # Footer with Creator Info (always at the bottom)
#     st.markdown("<p style='text-align: center; font-size: 12px; margin-top: 40px;'>Made by Dikshay Gusain</p>",
#                 unsafe_allow_html=True)
#
#
# # Run the main app
# if __name__ == "__main__":
#     main()