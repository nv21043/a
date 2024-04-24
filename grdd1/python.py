from flask import Flask, render_template, request, redirect, url_for, send_file ,session
from data_handler import get_students, update_student_data
import yagmail
import qrcode
from io import BytesIO
import os
import base64
import cv2
import face_recognition
from PIL import Image
from pyzbar.pyzbar import decode
from flask import jsonify 
import webbrowser
import pyautogui
import time
import qrcode
import cv2
from flask import Flask, render_template, request, redirect, url_for
import webbrowser
import pyautogui
import time
import qrcode
import cv2
import os
# Define Flask app instance
app = Flask(__name__)
secret_key = os.urandom(24)
students = get_students() 
app = Flask(__name__)
website_url = "https://sis.nvtc.edu.bh/site/login"  # Corrected the website URL
main_page_url = "/"  # Flask main page URL

# Set the coordinates where you want to move the mouse
username_coords = (624, 342)
password_coords = (530, 388)
submit_coords = (820, 431)

# Function to read QR code from an image file
def read_qr_code_from_image(image_path):
    img = cv2.imread(image_path)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(img)
    return data

# Function to read QR code from camera
def read_qr_code_from_camera():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    while True:
        _, frame = cap.read()
        data, _, _ = detector.detectAndDecode(frame)
        if data:
            break
        cv2.imshow('QR Code Reader', frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return data

# Read QR code from an uploaded image file
def read_qr_code_from_upload(file):
    file.save('uploaded_image.png')  # Save the uploaded file
    return read_qr_code_from_image('uploaded_image.png')

@app.route('/loginqr')
def index():
    return render_template('qr.html')

@app.route('/loginin', methods=['POST'])
def loginn():
    # Check if 'file' field exists in request.files
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            username, password = read_qr_code_from_upload(file).split(',')
            # Set the mouse cursor to be invisible
            pyautogui.FAILSAFE = False  # Disable failsafe
            # Open the website in Google Chrome
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
            webbrowser.get(chrome_path).open(website_url)
            # Delay before starting the automation (in seconds)
            time.sleep(3)
            # Move the mouse really fast and enter the username
            pyautogui.moveTo(username_coords, duration=0)
            # Click and type the username
            pyautogui.click()
            pyautogui.typewrite(username)
            # Move the mouse really fast and enter the password
            pyautogui.moveTo(password_coords, duration=0)
            # Click and type the password
            pyautogui.click()
            pyautogui.typewrite(password)
            # Move the mouse really fast and press the Enter key
            pyautogui.moveTo(submit_coords, duration=0)
            pyautogui.press('enter')
            # Redirect back to the main page
            return redirect(url_for('index'))
    # If no file uploaded or file is empty, redirect to the main page
    return redirect(url_for('index'))


@app.route('/detect_face', methods=['GET'])
def detect_face():
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
        return jsonify({'result': 'Error: Could not open video capture.'})

    # Flag to indicate if a face has been detected
    face_detected = False
    detected_nv = None  # Define detected_nv before the loop

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Check if the frame is empty
        if not ret:
            return jsonify({'result': 'Error: Empty frame.'})

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
                    face_detected = True
                    detected_nv = nv  # Update detected_nv when a face is detected
                    break

        # If a face is detected, break out of the loop
        if face_detected:
            break

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    video_capture.release()
    cv2.destroyAllWindows()
    if detected_nv:
        return jsonify({'result': 'Success', 'nv_number': detected_nv})
    else:
        return jsonify({'result': 'No face detected'})

SENDER_EMAIL = "nvtcbookingsystem@gmail.com"
SENDER_APP_PASSWORD = "Nvtc@1234"# Replace with your sender app password

def generate_qr_code(username, password):
    # Combine username and password into a single string
    data = f"{username},{password}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    return img

 # Retrieve students data

# Modify the route function for /qr_generator



@app.route('/qr_generator', methods=['GET', 'POST'])
def qr_generator():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        qr_code_img = generate_qr_code(username, password)
        
        # Save the image to a BytesIO buffer
        img_buffer = BytesIO()
        qr_code_img.save(img_buffer, format='PNG')
        
        # Encode the image buffer to base64
        qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return render_template('qr_generator.html', qr_code=qr_code_base64)
    return render_template('qr_generator.html')

# Main route
# Main route
@app.route('/')
def main_page():
    nv_number = session.get('nv_number')
    student_name = None
    if nv_number in students:
        student_name = students[nv_number]['Name']
    return render_template('main.html', nv_number=nv_number, student_name=student_name)

# Route to access the sending email page
@app.route('/send_email_page')
def send_email_page():
    return render_template('send_email_page.html', specialties=TEAM_MEMBERS.keys())

# Display student's classes route
@app.route('/display_classes', methods=['POST'])
def display_classes():
    nv_number = preprocess_nv_number(request.form['nv_number'])
    student_data = students.get(nv_number)
    if student_data:
        return render_template('class_selection.html', student_name=student_data['Name'], classes=student_data['Classes'])
    else:
        return render_template('nv_number_not_found.html', nv_number=nv_number)
# Add route for displaying student timetable
    
@app.route('/timetable/<nv_number>')
def timetable(nv_number):
    student_data = students.get(nv_number)
    if student_data:
        return render_template('timetable.html', student_name=student_data['Name'], timetable=student_data['Timetable'])
    else:
        return render_template('nv_number_not_found.html', nv_number=nv_number)

# Check class route
@app.route('/check_class', methods=['POST'])
def check_class():
    subject = request.form['subject']
    class_name = get_class_name(subject)
    # You can add logic here to fetch the image based on the subject if needed
    image_filename = f"{subject.lower()}.png"  # Example image filename
    video_filename = f"{subject.lower()}.mp4"  # Example video filename
    students_data = get_students()
    # Pass the students data, subject, class name, image filename, and video filename to the template
    return render_template('class_result.html', subject=subject, class_name=class_name, image_filename=image_filename, video_filename=video_filename, students=students_data)

@app.route('/admin_panel')
def admin_panel():
    students = get_students()  # Retrieve students data
    return render_template('admin_panel.html', students=students)

# Route to update student data
@app.route('/update_student', methods=['POST'])
def update_student():
    nv_number = request.form['nv_number']
    updated_data = {
        'Name': request.form['name'],
        # Add other updated fields here
    }
    update_student_data(nv_number, updated_data)
    # Redirect to admin panel after updating
    return redirect(url_for('admin_panel'))

# Route for handling NV number submission

@app.route('/login', methods=['POST'])
def login():
    nv_number = request.form.get('nv_number')
    if nv_number:
        session['nv_number'] = nv_number
        return 'Success'  # Or you can return a redirect to the main page
    else:
        return 'Failure'  # Handle failure case as needed
    
# Authentication function
def authenticate_nv_number(nv_number):
    # Check if the NV number exists in the database
    return nv_number in students
@app.route('/logout')
def logout():
    session.pop('nv_number', None)
    return redirect(url_for('main_page'))

# Route to render the FAQ page
@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/nv_number_form')
def nvnumberform():
    return render_template('nv_number_form.html')

# Define team members
TEAM_MEMBERS = {
    "Academic": {
        1: {"name": "Nabih Aziz", "email": "nabih.aziz@example.com"},
        2: {"name": "Dr. Mussab Z. Aswad", "email": "nv21053@nvtc.edu.bh"},
        3: {"name": "Basma Mohamed Al Balooshi", "email": "basma.balooshi@example.com"},
        4: {"name": "Sana Abdulrahman", "email": "nv21043@nvtc.edu.bh"}
    },
    "Vocational": {
        1: {"name": "Franklin F. Narag Bosi", "email": "franklin.bosi@example.com"},
        2: {"name": "Raghavendra Shenoy", "email": "raghavendra.shenoy@example.com"}
    }
}

# Define the send_email function to send meeting requests
def send_email(recipient, subject, body):
    try:
        with yagmail.SMTP(SENDER_EMAIL, SENDER_APP_PASSWORD) as yag:
            yag.send(recipient, subject, body)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def preprocess_nv_number(nv_number):
    # Remove any non-alphanumeric characters and convert to uppercase
    nv_number = ''.join(char for char in nv_number if char.isalnum()).upper()
    # Add "NV" prefix if missing
    if not nv_number.startswith("NV"):
        nv_number = "NV" + nv_number
    return nv_number

# Function to retrieve class name based on subject
def get_class_name(subject):
    for student_data in students.values():
        class_name = student_data['Classes'].get(subject)
        if class_name:
            return class_name
    return None
@app.route('/qr_options')
def qr_options():
    # Logic to render the QR options page
    return render_template('qr_options.html')

# Route to select specialty
@app.route('/select_specialty')
def select_specialty():
    display_specialties()
    return render_template('select_specialty.html', specialties=TEAM_MEMBERS.keys())

# Route to select team member
@app.route('/select_team_member', methods=['POST'])
def select_team_member():
    specialty = request.form['specialty']
    team_members = TEAM_MEMBERS.get(specialty, {})
    return render_template('select_team_member.html', specialty=specialty, team_members=team_members)

# Route to send meeting request
@app.route('/send_meeting_request', methods=['POST'])
def send_meeting_request():
    team_member_email = request.form['team_member_email']
    guest_name = request.form['guest_name']
    meeting_time = request.form['meeting_time']
    subject = f"Meeting Request from {guest_name}"
    body = f"Hi,\n\nMr/s {guest_name} would like to meet you at {meeting_time}.\n\nBest regards,\nYour Guest"
    send_email(team_member_email, subject, body)
    return redirect(url_for('index'))

def display_specialties():
    print("Available Specialties:")
    for i, specialty in enumerate(TEAM_MEMBERS, start=1):
        print(f"{i}. {specialty}")

def choose_specialty():
    while True:
        try:
            specialty_choice = int(input("Enter the number of your preferred specialty: "))
            specialties = list(TEAM_MEMBERS.keys())
            if 1 <= specialty_choice <= len(specialties):
                return specialties[specialty_choice - 1]
            else:
                print("Invalid choice. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def choose_team_member(specialty):
    team_member_list = TEAM_MEMBERS.get(specialty, {})
    if not team_member_list:
        print(f"No team members found for {specialty}.")
        return

    print(f"Team members in {specialty}:")
    for num, member in team_member_list.items():
        print(f"{num}. {member['name']} ({member['email']})")

    while True:
        try:
            team_member_choice = int(input("Enter the number of your preferred team member: "))
            if team_member_choice in team_member_list:
                selected_member = team_member_list[team_member_choice]
                print(f"Selected team member: {selected_member['name']} ({selected_member['email']})")

                # Get guest name and meeting time
                guest_name = input("Enter your name: ")
                meeting_time = input("Enter the meeting time (e.g., 2:00 PM): ")

                # Compose email
                subject = f"Meeting Request from {guest_name}"
                body = f"Hi {selected_member['name']},\n\nMr/s {guest_name} would like to meet you at {meeting_time}.\n\nBest regards,\nYour Guest"

                # Send email
                send_email(selected_member['email'], subject, body)
                break
            else:
                print("Invalid choice. Please enter a valid team member number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    app.run()(debug=False,host='0.0.0.0')