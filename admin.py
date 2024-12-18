import os
import streamlit as st
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Load environment variables from .env
load_dotenv()

# Firebase Initialization
def initialize_firebase():
    firebase_cred_path = os.getenv("FIREBASE_CRED_PATH")
    if not firebase_cred_path:
        st.error("Firebase credential path is missing!")
        return None
    cred = credentials.Certificate(firebase_cred_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Function to fetch subscriptions from Firestore
def fetch_subscriptions(db):
    try:
        subscriptions_ref = db.collection("subscriptions")  # Collection name
        docs = subscriptions_ref.stream()
        users = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        return users
    except Exception as e:
        st.error(f"Error fetching subscriptions: {e}")
        return []

# Function to fetch disaster reports from Firestore
def fetch_disaster_reports(db):
    try:
        disaster_ref = db.collection("disaster_reports")  # Collection name
        docs = disaster_ref.stream()
        reports = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        return reports
    except Exception as e:
        st.error(f"Error fetching disaster reports: {e}")
        return []

# Function to send bulk email alerts with embedded logo and footer
def send_bulk_emails(email_list, subject, message):
    try:
        sender_email = os.getenv("EMAIL_ID")
        sender_password = os.getenv("EMAIL_PASSWORD")
        logo_path = os.getenv("LOGO_PATH")

        if not sender_email or not sender_password or not logo_path:
            st.error("Email credentials or logo path is missing!")
            return False

        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Footer content to be added at the bottom of the email
        footer = """
        <div style="text-align: center; font-size: 12px; color: #888; margin-top: 20px;">
            © 2024 HCL-GeoSense AI | Developed by Team Indriyaan | Powered by HCLTech
        </div>
        """

        # Email body with HTML content
        html_message = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <p>{message}</p>
            <img src="cid:company_logo" alt="Company Logo" style="width: 100px; height: auto;" />
            {footer}
        </body>
        </html>
        """

        # Open image file and attach it
        with open(logo_path, "rb") as logo_file:
            logo_data = logo_file.read()

        # Create the email message
        msg = MIMEMultipart("related")
        msg["From"] = sender_email
        msg["To"] = ", ".join(email_list)
        msg["Subject"] = subject

        # Attach the HTML message
        msg.attach(MIMEText(html_message, "html"))

        # Attach the image
        image = MIMEImage(logo_data, name="company_logo.png")
        image.add_header('Content-ID', '<company_logo>')  # Add a Content-ID header to reference the image in HTML
        msg.attach(image)

        # Sending the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email to each recipient
        for email in email_list:
            server.sendmail(sender_email, email, msg.as_string())

        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending emails: {e}")
        return False

# Admin login validation
def validate_admin_login(email, password):
    admin_email = os.getenv("EMAIL_ID")
    admin_password = os.getenv("EMAIL_PASSWORD")
    return email == admin_email and password == admin_password

# Main function for Streamlit App
def main():
    # Initialize Firebase Firestore client
    db = initialize_firebase()
    if not db:
        return
    
    st.title("HCL-GeoSense AI - Admin Dashboard")

    # Initialize session state for admin login
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

    if not st.session_state.is_logged_in:
        # Admin Login
        st.subheader("Admin Login")
        admin_email = st.text_input("Enter Admin Email")
        admin_password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("Login"):
            if validate_admin_login(admin_email, admin_password):
                st.session_state.is_logged_in = True
                st.success("Login Successful!")
            else:
                st.error("Invalid email or password.")
    else:
        # Admin Dashboard options
        st.subheader("Admin Dashboard")
        option = st.selectbox("Select an option", ["List of Users", "Disaster Reports"])

        if option == "List of Users":
            # Fetch and display users
            users = fetch_subscriptions(db)
            if users:
                st.write(f"**Total Registered Users:** {len(users)}")
                
                # Filter users based on location
                location_filter = st.text_input("Filter Users by Location (e.g., City, Country)")
                if location_filter:
                    users = [user for user in users if location_filter.lower() in user.get("location", "").lower()]

                # Remove sensitive fields like password before displaying
                for user in users:
                    user.pop("password", None)  # Remove the 'password' field if it exists
                
                # Convert user list to a DataFrame for tabular display
                user_df = pd.DataFrame(users)
                st.dataframe(user_df)  # Display users as a table

                # Send email alert
                st.subheader("Send Alert Email to Filtered Users")
                subject = st.text_input("Enter Email Subject")
                message = st.text_area("Enter Email Message")

                if st.button("Send Alert Email"):
                    if not subject or not message:
                        st.error("Please enter both subject and message.")
                    else:
                        email_list = [user["email"] for user in users if user.get("email")]  # Ensure non-empty emails
                        if send_bulk_emails(email_list, subject, message):
                            st.success("Emails sent successfully!")
                        else:
                            st.error("Failed to send emails.")
            else:
                st.write("No registered users found.")

        elif option == "Disaster Reports":
            # Fetch and display disaster reports
            reports = fetch_disaster_reports(db)
            if reports:
                st.write(f"**Total Disaster Reports:** {len(reports)}")
                report_df = pd.DataFrame(reports)
                st.dataframe(report_df)  # Display reports as a table
            else:
                st.write("No disaster reports found.")

        # Logout button
        if st.button("Logout"):
            st.session_state.is_logged_in = False
            st.success("Logged out successfully.")

# Run the app
if __name__ == "__main__":
    main()
