import cv2
import face_recognition

# Define the data with NV numbers and corresponding names
nv_data = {
    "NV21039": "Sayed Ahmed Mohmed Ahmed Marhoom",
    "NV21040": "Turki Khaled Ali Aljashari",
    "NV21041": "Humood Rashed Ali Alkaabi",
    "NV21042": "Rashed Abdulrahman Jasim Bumetea",
    "NV21043": "Saad Adel Saad Alateya",
    "NV21044": "Saud Faisal Hamad Aldoseri",
    "NV21045": "Sultan Ali Sultan Fakhroo",
    "NV21046": "Tariq Salah Ebrahim Alyasi",
    "NV21047": "Abdulaziz Mohamed Abdulla Yusuf",
    "NV21048": "Abdulla Mohamed Abdulla Almalki",
    "NV21049": "Hussain Ali Ebrahim Alsamaheeji",
    "NV21050": "Ali Ahmed Mansoor Makhlooq",
    "NV21051": "Ali Khalil Jaafar Alqassab",
    "NV21052": "Ali Mohamed Abdulredha Abdulla",
    "NV21053": "Ali Mohammad Yaqoob Albalushi",
    "NV21054": "Isa Mohamed Ali Alrowaiei",
    "NV21055": "Mahmood Mohamed Saber Hasan",
    "NV21056": "Yousif Abdulmajeed Ghulam Abdali",
    "NV21057": "Hasan Isa Abbas Almanoo"
}

# Load the known faces
# Load the known faces
known_faces = []
for nv, name in nv_data.items():
    try:
        face_image = face_recognition.load_image_file(nv.lower() + ".jpg")
        face_encoding = face_recognition.face_encodings(face_image)[0]
        known_faces.append((nv, face_encoding))
    except FileNotFoundError:
        continue

# Initialize video capture
video_capture = cv2.VideoCapture(0)

# Check if the video capture is successful
if not video_capture.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Flag to indicate if a face has been detected
face_detected = False

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Check if the frame is empty
    if not ret:
        print("Error: Empty frame.")
        break

    # Resize the frame to speed up face recognition
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    for face_encoding in face_encodings:
        # Compare face encoding with known encodings
        for nv, known_encoding in known_faces:
            matches = face_recognition.compare_faces([known_encoding], face_encoding)
            if matches[0] and not face_detected:
                print(nv)
                face_detected = True
                break

    # If a face is detected, break out of the loop
    if face_detected:
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
video_capture.release()
cv2.destroyAllWindows()
