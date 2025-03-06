import pyautogui
import time
import os
import face_recognition
import sqlite3
import requests
import jwt  # Ensure pyjwt is installed
import numpy as np
import keyboard
from datetime import datetime, timedelta, timezone

# Zoom JWT Credentials
ZOOM_API_KEY = "9jA60H3aRAa_JZoW4_TLpQ"  # Replace with your Zoom API Key
ZOOM_API_SECRET = "p9ogiyw48L9sxSTmEi6Luwvw5RJCbH8f"  # Replace with your Zoom API Secret

# Screenshot folder setup
base_dir = 'zoom_screenshots'
today_date = datetime.now().strftime('%Y-%m-%d')
screenshot_dir = os.path.join(base_dir, today_date)
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# SQLite Database setup
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create the ATTENDANCE table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS ATTENDANCE (
    ID TEXT,
    Date TEXT,
    Status TEXT
)
""")
conn.commit()

# Load the known faces for face recognition
known_face_encodings = []
known_face_ids = []


def load_known_faces():
    if not os.path.exists('Training_images'):
        print("Training_images folder is missing!")
        return

    image_files = os.listdir('Training_images')
    for file in image_files:
        img = face_recognition.load_image_file(f'Training_images/{file}')
        encoding = face_recognition.face_encodings(img)[0]
        known_face_encodings.append(encoding)
        user_id = os.path.splitext(file)[0]
        known_face_ids.append(user_id)


def mark_attendance(user_id):
    today_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM ATTENDANCE WHERE ID = ? AND Date = ?", (user_id, today_date))
    record = cursor.fetchone()

    if not record:
        cursor.execute("INSERT INTO ATTENDANCE (ID, Date, Status) VALUES (?, ?, ?)", (user_id, today_date, "Present"))
        conn.commit()
        print(f"Attendance marked for ID {user_id} on {today_date}")


def get_jwt_token():
    # Use your Zoom API Key and Secret to generate JWT token
    payload = {
        "iss": ZOOM_API_KEY,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)  # Updated for timezone-aware datetime
    }
    token = jwt.encode(payload, ZOOM_API_SECRET, algorithm='HS256')
    return token


def create_zoom_meeting(jwt_token):
    url = f"https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }
    start_time = datetime.utcnow().isoformat() + 'Z'  # Ensure correct datetime format
    payload = {
        "topic": "Class Meeting",
        "type": 2,  # Scheduled meeting
        "start_time": start_time,
        "duration": 60,
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


def main():
    load_known_faces()
    interval = 2

    print("Press 'c' to create a Zoom meeting.")
    print("Press 'q' to stop the program.")

    jwt_token = get_jwt_token()
    if not jwt_token:
        print("Exiting program due to failed JWT token generation.")
        exit()

    try:
        while True:
            if keyboard.is_pressed('c'):
                meeting_link = create_zoom_meeting(jwt_token)
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


if __name__ == "__main__":
    main()
