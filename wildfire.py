import cv2
import numpy as np
import smtplib
import pygame
import threading
import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EMAIL_ID = os.getenv("EMAIL_ID")  # Your email address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # App Password
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")  # Firebase credentials JSON path

# Streamlit UI
def setup_streamlit_ui():
    st.title("HCL-GeoSense AI Live Wild-Fire Detection & Alert System 🔥")
    location_input = st.text_input("Enter your location:", "")
    st.info("This system will detect Wild-Fire and notify users in the specified location.")
    return location_input

# Firebase initialization (only if not already initialized)
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Alarm and Email Status
Alarm_Status = False
Email_Status = False
Fire_Reported = 0

# Function to play alarm sound
def play_alarm_sound_function():
    try:
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('alarm-sound.mp3')  # Ensure the path to 'alarm-sound.mp3' is correct
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Keep playing
            time.sleep(1)
    except Exception as e:
        print(f"Error playing alarm sound: {e}")

def send_mail_function(location, db):
    global Email_Status
    try:
        recipient_emails = []
        # Query Firebase for users subscribed to the specified location using 'where'
        users_ref = db.collection('subscriptions')
        docs = users_ref.where("location", "==", location).stream()  # Correct method to filter documents
        print(f"Fetching email addresses for location: {location}...")

        for doc in docs:
            user_data = doc.to_dict()
            email = user_data.get('email')
            if email:
                recipient_emails.append(email)

        print(f"Found emails: {recipient_emails}")

        # Send email to all users in the specified location
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ID, EMAIL_PASSWORD)
        
        for email in recipient_emails:
            message = f"""Subject: HCL-GeoSense AI Wild-Fire Alert! \n\n
            Warning: Fire detected in {location}!
            
            Precautions to follow:
            1. Evacuate the building immediately and move to a safe location.
            2. Avoid using elevators and follow emergency exit signs.
            
            © 2024 HCL-GeoSense AI | Developed by Team Indriyaan | Powered by HCLTech
    
            """
            server.sendmail(EMAIL_ID, email, message)
            print(f"Email sent to {email}")

        server.close()
        print("All emails sent successfully.")
        # Show success message in Streamlit UI after sending emails
        Email_Status = True
        st.success(f"Fire detected! Emails have been sent to all users in {location}.")
    except Exception as e:
        print(f"Error sending email: {e}")
        st.error("Failed to send email.")

# OpenCV Video Stream for Fire Detection
def fire_detection(location_input, db):
    global Alarm_Status, Email_Status, Fire_Reported

    video = cv2.VideoCapture(0)  # Webcam live feed
    stframe = st.empty()  # Streamlit placeholder for displaying video

    while True:
        grabbed, frame = video.read()
        if not grabbed:
            break

        frame = cv2.resize(frame, (960, 540))
        blur = cv2.GaussianBlur(frame, (21, 21), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        # Fire color range (tweak if needed)
        lower = np.array([18, 50, 50], dtype="uint8")
        upper = np.array([35, 255, 255], dtype="uint8")

        mask = cv2.inRange(hsv, lower, upper)
        output = cv2.bitwise_and(frame, hsv, mask=mask)

        no_red = cv2.countNonZero(mask)

        # If fire is detected based on threshold
        if int(no_red) > 15000:  # Fire threshold
            Fire_Reported += 1
            if not Alarm_Status:
                print("Fire detected! Playing alarm sound...")
                threading.Thread(target=play_alarm_sound_function).start()
                Alarm_Status = True

            if not Email_Status and location_input:
                print("Sending email notifications...")
                threading.Thread(target=send_mail_function, args=(location_input, db)).start()

            # Displaying a message on the video feed
            cv2.putText(frame, "Fire Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            # Draw bounding box around the detected fire areas (optional)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 500:  # Minimum area for contour to be considered
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(frame, "Fire Area", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Display success message on Streamlit UI
            st.success("🔥 Fire detected! Alarm triggered and email sent. 🔥")

        # Stream video to Streamlit UI
        stframe.image(frame, channels="BGR", use_container_width=True)

        # Capture every 5 seconds
        time.sleep(5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

# Main function to run the application
def main():
    location_input = setup_streamlit_ui()  # Set up Streamlit UI
    if location_input:
        st.success(f"Monitoring for fire at location: {location_input}")
        db = initialize_firebase()  # Initialize Firebase
        if st.button("Start Fire Detection"):
            fire_detection(location_input, db)
    else:
        st.warning("Please enter a location to start fire detection.")

# Run the main function
if __name__ == "__main__":
    main()
