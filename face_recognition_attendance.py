import cv2  # For accessing the webcam and image processing.
import numpy as np   # For numerical operations and array handling.
import face_recognition  # For face detection and recognition.
import os  # For interacting with the operating system, like reading file directories.
import sqlite3   # For database management (attendance records).
from datetime import datetime   # For handling and formatting date and time.

# Path to the folder containing training images
path = r"Training_images"
images = []
classNames = []

# Load training images
myList = os.listdir(path)
print(f"Training images: {myList}")
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

print(f"Class names: {classNames}")

# Function to encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except IndexError:
            print("Face not detected in one of the images. Skipping...")
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Initialize database connection
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create ATTENDANCE table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS ATTENDANCE (
    ID INTEGER,
    Name TEXT,
    Date TEXT,
    Time TEXT,
    Status TEXT
)
""")
conn.commit()

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    exit()

attendance_log = {}

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame.")
        break

    # Resize and preprocess the frame
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect and encode faces
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.5)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex] and faceDis[matchIndex] < 0.5:  # High accuracy check
            user_id = int(classNames[matchIndex])  # Assume ID is the image name (as an integer)

            # Fetch the student's name from the database
            cursor.execute("SELECT Name FROM STUDENTS WHERE Id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                name = result[0]  # Retrieve the name from the database
            else:
                name = f"Unknown ({user_id})"  # Fallback if ID is not found in the database

            current_time = datetime.now()
            date_str = current_time.strftime("%Y-%m-%d")
            time_str = current_time.strftime("%H:%M:%S")

            # Check if the user has already been marked present today
            cursor.execute("SELECT * FROM ATTENDANCE WHERE ID = ? AND Date = ?", (user_id, date_str))
            existing_record = cursor.fetchone()

            if not existing_record:  # If no record exists for today
                # Insert attendance into the database
                conn.execute("INSERT INTO ATTENDANCE (ID, Name, Date, Time, Status) VALUES (?, ?, ?, ?, ?)",
                             (user_id, name, date_str, time_str, "Present"))
                conn.commit()
                print(f"Attendance marked for {name} on {date_str}")
            else:
                print(f"{name} has already been marked present today.")

            # Draw bounding box and name on the face
            y1, x2, y2, x1 = faceLoc #contain the location of the detected face(tuples)[top,right,bottom,left]
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    # Display the webcam feed
    cv2.imshow('Webcam', img)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()

