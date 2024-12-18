import smtplib
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Fetch the variables from the .env file
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH')
EMAIL_ID = os.getenv('EMAIL_ID')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Initialize Firebase Admin SDK only if it hasn't been initialized yet
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Function to validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to send email confirmation after signup
def send_email_confirmation(user_email):
    sender_email = EMAIL_ID
    sender_password = EMAIL_PASSWORD
    receiver_email = user_email
    subject = "Registration Confirmation - HCL-GeoSense AI"
    body = """
    <html>
    <body>
    <h2>Welcome to HCL-GeoSense AI!</h2>
    <p>Your registration was successful. Thank you for joining us!</p>
    <p>Best regards,<br>HCL-GeoSense AI Team</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        st.success(f"Confirmation email sent to {receiver_email}!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Function to sign up the user and add to Firebase Firestore
def signup_user(name, email, password, location):
    try:
        users_ref = db.collection('subscriptions')
        query = users_ref.where('email', '==', email).get()

        if query:
            st.error("User already exists with this email!")
            return None

        new_user_ref = users_ref.add({
            'name': name,
            'email': email,
            'password': password,  # In production, passwords must be hashed
            'location': location
        })

        st.success(f"User created successfully with email: {email}")
        send_email_confirmation(email)
        return new_user_ref
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return None

# Function to log in the user
def login_user(email, password):
    try:
        users_ref = db.collection('subscriptions')
        query = users_ref.where('email', '==', email).get()

        if not query:
            st.error("User not found!")
            return None

        user = query[0].to_dict()

        if user['password'] == password:
            st.success(f"Welcome, {user['name']}!")
            return user
        else:
            st.error("Invalid password!")
            return None
    except Exception as e:
        st.error(f"Error during login: {e}")
        return None

# Function to submit disaster report
def submit_disaster_report(name, mail_id, num_people, event_type, medicine_required, medicine_name, food_required, address):
    try:
        db.collection('disaster_reports').add({
            'name': name,
            'mail_id': mail_id,
            'num_people': num_people,
            'event_type': event_type,
            'medicine_required': medicine_required,
            'medicine_name': medicine_name if medicine_required else '',
            'food_required': food_required,
            'address': address,
            'timestamp': datetime.datetime.now()
        })
        st.success("Disaster report submitted successfully!")
    except Exception as e:
        st.error(f"Error submitting disaster report: {e}")

# Function to display disaster alerts
def display_disaster_alerts():
    st.title("Disaster Alerts")
    st.write("Here are the current disaster alerts:")
    st.write("- Floods in coastal regions.")
    st.write("- Earthquake warnings in the northern part of the country.")
    st.write("- Wildfires reported in the western forest areas.")
    st.write("- Tsunami watch along the Pacific coast.")
    st.write("- Hurricane approaching the southern region.")
    st.write("Stay tuned for more updates.")

# Dashboard for logged-in user
def dashboard(user):
    st.title("HCL-GeoSense AI - User Dashboard")
    st.write(f"Welcome, {user['name']}!")

    option = st.selectbox("Select an option", ["View Disaster Alerts", "Submit Disaster Report"])

    if option == "View Disaster Alerts":
        display_disaster_alerts()

    elif option == "Submit Disaster Report":
        st.subheader("Disaster Report Form")
        name = st.text_input("Your Name")
        mail_id = st.text_input("Email")
        num_people = st.number_input("Number of People", min_value=1, step=1)
        event_type = st.selectbox("Type of Event", ["Flood", "Earthquake", "Tornado", "Wildfire", "Hurricane", "Tsunami"])
        medicine_required = st.radio("Do you need any medicine?", ("Yes", "No"))
        medicine_name = st.text_input("Medicine Name") if medicine_required == "Yes" else ""
        food_required = st.radio("Do you require food?", ("Yes", "No"))
        address = st.text_input("Address")

        if st.button("Submit Report"):
            if name and mail_id and address:
                submit_disaster_report(name, mail_id, num_people, event_type, medicine_required == "Yes", medicine_name, food_required == "Yes", address)
            else:
                st.warning("Please fill in all required fields.")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# Streamlit UI for login, sign-up, and dashboard
def main():
    st.title("HCL-GeoSense AI - Login / Sign-up")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None

    if st.session_state.authenticated:
        dashboard(st.session_state.user)
    else:
        option = st.selectbox("Select an option", ["Login", "Sign up"])

        if option == "Sign up":
            name = st.text_input("Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            location = st.text_input("Location")

            if st.button("Sign Up"):
                if name and email and password and location:
                    if is_valid_email(email):
                        signup_user(name, email, password, location)
                    else:
                        st.warning("Please enter a valid email address.")
                else:
                    st.warning("Please fill all fields.")

        elif option == "Login":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if email and password:
                    user = login_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.rerun()
                else:
                    st.warning("Please enter email and password.")

if __name__ == "__main__":
    main()
