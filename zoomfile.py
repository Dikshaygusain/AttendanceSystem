import pyautogui
import time
import os
import face_recognition
import sqlite3
import requests
from datetime import datetime
import numpy as np
import keyboard
import webbrowser
import urllib.parse
import requests

# Zoom OAuth Credentials
ZOOM_CLIENT_ID = "4wZmddQ9TJ6tXG4IAYfT3Q"  # Client ID (OAuth)
ZOOM_CLIENT_SECRET = "Xc4pjkOGFNok8FzPLigOBERLRfkhlZNP"  # Client Secret (OAuth)
ZOOM_REDIRECT_URI = "http://localhost:5000/callback" # Replace with your callback URL
ZOOM_USER_ID = "dikshaygusain9568@gmail.com"  # Replace with your Zoom email address (or User ID)


# Folder to store the screenshots
base_dir = 'zoom_screenshots'
today_date = datetime.now().strftime('%Y-%m-%d')
screenshot_dir = os.path.join(base_dir, today_date)

# Check if folder exists, create if not
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# SQLite Database setup
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()


# Function to mark attendance in the database
def mark_attendance(user_id):
    today_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM ATTENDANCE WHERE ID = ? AND Date = ?", (user_id, today_date))
    record = cursor.fetchone()

    if not record:
        cursor.execute("INSERT INTO ATTENDANCE (ID, Date, Status) VALUES (?, ?, ?)", (user_id, today_date, "Present"))
        conn.commit()
        print(f"Attendance marked for ID {user_id} on {today_date}")


# Load the known faces for face recognition
known_face_encodings = []
known_face_ids = []


def load_known_faces():
    image_files = os.listdir('Training_images')
    for file in image_files:
        img = face_recognition.load_image_file(f'Training_images/{file}')
        encoding = face_recognition.face_encodings(img)[0]
        known_face_encodings.append(encoding)
        user_id = os.path.splitext(file)[0]
        known_face_ids.append(user_id)


# Function to get OAuth Access Token
def get_oauth_access_token():
    # OAuth token URL
    token_url = "https://zoom.us/oauth/token"

    # Get authorization code from the callback URL (this part needs user action)
    authorization_code = input("Enter the authorization code from the callback URL: ")

    # Prepare data for token exchange
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": ZOOM_REDIRECT_URI,
    }

    # Send a POST request to get the access token
    response = requests.post(token_url, data=data, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET))

    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info["access_token"]
        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Failed to get Access Token: {response.json()}")
        return None


# Function to create a Zoom meeting using OAuth access token
def create_zoom_meeting(access_token):
    url = f"https://api.zoom.us/v2/users/{ZOOM_USER_ID}/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "topic": "Class Meeting",
        "type": 2,
        "start_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "duration": 60,  # Meeting duration in minutes
        "settings": {
            "join_before_host": True,
            "participant_video": True,
        },
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        meeting_details = response.json()
        meeting_link = meeting_details.get("join_url")
        print(f"Meeting created successfully. Link: {meeting_link}")
        return meeting_link
    else:
        print("Failed to create Zoom meeting:", response.json())
        return None


# Main program
load_known_faces()
interval = 2

try:
    print("Press 'c' to create a Zoom meeting.")
    print("Press 'q' to stop the program.")

    # Step 1: Get OAuth Access Token (only need to run once, store it for future use)
    access_token = get_oauth_access_token()

    if not access_token:
        print("Exiting program due to failed access token generation.")
        exit()

    while True:
        if keyboard.is_pressed('c'):
            meeting_link = create_zoom_meeting(access_token)
            if meeting_link:
                print(f"Share this link with students: {meeting_link}")

        if keyboard.is_pressed('q'):
            print("Exiting program...")
            break

        timestamp = datetime.now().strftime('%H-%M-%S')
        screenshot = pyautogui.screenshot()
        screenshot = screenshot.resize((640, 480))
        screenshot.save(f"{screenshot_dir}/screenshot_{timestamp}.png")
        print(f"Captured screenshot {timestamp}")

        img = screenshot.convert('RGB')
        face_locations = face_recognition.face_locations(np.array(img))
        face_encodings = face_recognition.face_encodings(np.array(img), face_locations)

        for encoding, location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, encoding)

            if True in matches:
                match_index = matches.index(True)
                user_id = known_face_ids[match_index]
                mark_attendance(user_id)

        time.sleep(interval)

except KeyboardInterrupt:
    print("Program interrupted manually.")

finally:
    conn.close()
    print("Database connection closed.")

# import pyautogui
# import time
# import os
# import face_recognition
# import sqlite3
# from datetime import datetime
# import numpy as np
# import keyboard
#
# # Folder to store the screenshots
# base_dir = 'zoom_screenshots'
# today_date = datetime.now().strftime('%Y-%m-%d')
# screenshot_dir = os.path.join(base_dir, today_date)
#
# # Check if folder exists, create if not
# if not os.path.exists(screenshot_dir):
#     os.makedirs(screenshot_dir)
#
# # SQLite Database setup
# conn = sqlite3.connect("attendance.db")
# cursor = conn.cursor()
#
#
# # Function to mark attendance in the database
# def mark_attendance(user_id):
#     # Get the current date
#     today_date = datetime.now().strftime('%Y-%m-%d')
#
#     # Check if the user is already marked present today
#     cursor.execute("SELECT * FROM ATTENDANCE WHERE ID = ? AND Date = ?", (user_id, today_date))
#     record = cursor.fetchone()
#
#     if not record:
#         # If the user is not marked present for today, insert their attendance
#         cursor.execute("INSERT INTO ATTENDANCE (ID, Date, Status) VALUES (?, ?, ?)", (user_id, today_date, "Present"))
#         conn.commit()
#         print(f"Attendance marked for ID {user_id} on {today_date}")
#
#
# # Load the known faces for face recognition
# known_face_encodings = []  # List to hold known face encodings
# known_face_ids = []  # List to hold the corresponding user IDs
#
#
# def load_known_faces():
#     # Load the images and create encodings (this is just an example, adjust as needed)
#     image_files = os.listdir('Training_images')  # Folder with images of users
#     for file in image_files:
#         img = face_recognition.load_image_file(f'Training_images/{file}')
#         encoding = face_recognition.face_encodings(img)[0]
#         known_face_encodings.append(encoding)
#         user_id = os.path.splitext(file)[0]  # Assuming filename is the user ID
#         known_face_ids.append(user_id)
#
#
# # Main program
# load_known_faces()  # Load known faces before starting
#
# interval = 2  # seconds
#
# try:
#     print("Press 'q' to stop the program.")
#     while True:
#         if keyboard.is_pressed('q'):  # Check if "q" is pressed
#             print("Exiting program...")
#             break  # Break the loop
#
#         timestamp = datetime.now().strftime('%H-%M-%S')
#
#         # Take screenshot and resize to speed up processing
#         screenshot = pyautogui.screenshot()
#         screenshot = screenshot.resize((640, 480))  # Resize the screenshot to reduce processing time
#         screenshot.save(f"{screenshot_dir}/screenshot_{timestamp}.png")
#         print(f"Captured screenshot {timestamp}")
#
#         # Convert screenshot to image format for face recognition
#         img = screenshot.convert('RGB')  # Convert to RGB
#
#         # Detect faces in the screenshot
#         face_locations = face_recognition.face_locations(np.array(img))
#         face_encodings = face_recognition.face_encodings(np.array(img), face_locations)
#
#         for encoding, location in zip(face_encodings, face_locations):
#             matches = face_recognition.compare_faces(known_face_encodings, encoding)
#
#             if True in matches:
#                 match_index = matches.index(True)
#                 user_id = known_face_ids[match_index]
#                 mark_attendance(user_id)  # Mark attendance in the database
#
#         time.sleep(interval)  # Wait before taking the next screenshot
#
# except KeyboardInterrupt:
#     print("Program interrupted manually.")
#
# finally:
#     # Ensure proper cleanup
#     conn.close()
#     print("Database connection closed.")
