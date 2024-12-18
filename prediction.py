import pandas as pd
import streamlit as st
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Tomorrow.io API Key (replace with your API key)
API_KEY = "XO188XoLwfJDR9mNkgCdzWHU0U0RM1Zz"

# Function to fetch current weather from Tomorrow.io
def fetch_current_weather(location):
    try:
        # Tomorrow.io endpoint
        url = f"https://api.tomorrow.io/v4/weather/realtime"
        params = {
            "location": location,
            "apikey": API_KEY,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        # Extract relevant details
        temperature = weather_data['data']['values']['temperature']
        humidity = weather_data['data']['values']['humidity']
        wind_speed = weather_data['data']['values']['windSpeed']
        cloud_cover = weather_data['data']['values']['cloudCover']

        # Convert cloud cover percentage to description
        if cloud_cover == 0:
            cloud_description = "Clear sky, no clouds."
            rain_chances = "No"
        elif 0 < cloud_cover <= 30:
            cloud_description = "Mostly clear with some clouds."
            rain_chances = "No"
        elif 30 < cloud_cover <= 60:
            cloud_description = "Partly cloudy."
            rain_chances = "Low"
        elif 60 < cloud_cover <= 90:
            cloud_description = "Mostly cloudy."
            rain_chances = "Moderate (possible)"
        else:
            cloud_description = "Overcast or fully cloudy sky."
            rain_chances = "High (likely)"

        return {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "cloud_description": cloud_description,
            "rain_chances": rain_chances,
        }
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# Function to send an email alert
def send_email(to_email, disaster_event, severity, data_summary, current_weather):
    # Email credentials (you should use environment variables or secure vault for real applications)
    from_email = "nagababusirigiri528@gmail.com"
    password = "gdwxrmzhitqbuuku"
    
    # Create the email subject
    subject = f"HCL-GeoSense AI Prediction for {disaster_event}"
    
    # Email body in HTML (for bilingual table format)
    email_body = f"""
    <html>
    <body>
    <h2>Disaster Severity Prediction</h2>

    <h3>Details of the disaster severity prediction:</h3>
    <table border="1">
        <tr>
            <th>Disaster Event (English)</th>
            <td>{disaster_event}</td>
        </tr>
        <tr>
            <th>Predicted Severity (English)</th>
            <td>{severity}</td>
        </tr>
        <tr>
            <th>Data Summary (English)</th>
            <td>{data_summary}</td>
        </tr>
    </table>

    <h3>ప్రाकृतिक విపత్తు తీవ్రత పర్యవేక్షణ:</h3>
    <table border="1">
        <tr>
            <th>ప్రाकृतिक విపత్తు (తెలుగు)</th>
            <td>{disaster_event}</td>
        </tr>
        <tr>
            <th>భవిష్యవాణి చేసిన తీవ్రత (తెలుగు)</th>
            <td>{severity}</td>
        </tr>
        <tr>
            <th>సమాచార సారాంశం (తెలుగు)</th>
            <td>{data_summary}</td>
        </tr>
    </table>

    <h3>Current Weather:</h3>
    <table border="1">
        <tr>
            <th>Temperature (°C) (English)</th>
            <td>{current_weather['temperature']}</td>
        </tr>
        <tr>
            <th>Humidity (%) (English)</th>
            <td>{current_weather['humidity']}</td>
        </tr>
        <tr>
            <th>Wind Speed (km/h) (English)</th>
            <td>{current_weather['wind_speed']}</td>
        </tr>
        <tr>
            <th>Cloud Description (English)</th>
            <td>{current_weather['cloud_description']}</td>
        </tr>
        <tr>
            <th>Rain Chances (English)</th>
            <td>{current_weather['rain_chances']}</td>
        </tr>
    </table>

    <h3>ప్రస్తుత వాతావరణం:</h3>
    <table border="1">
        <tr>
            <th>ఉష్ణోగ్రత (°C) (తెలుగు)</th>
            <td>{current_weather['temperature']}</td>
        </tr>
        <tr>
            <th>ఆర్ద్రత (%) (తెలుగు)</th>
            <td>{current_weather['humidity']}</td>
        </tr>
        <tr>
            <th>గాలివేగం (కిమీ/గంట) (తెలుగు)</th>
            <td>{current_weather['wind_speed']}</td>
        </tr>
        <tr>
            <th>మేఘ వివరణ (తెలుగు)</th>
            <td>{current_weather['cloud_description']}</td>
        </tr>
        <tr>
            <th>వర్షం అవకాశాలు (తెలుగు)</th>
            <td>{current_weather['rain_chances']}</td>
        </tr>
    </table>
    <p>Best regards,<br>HCL-GeoSense AI Team</p>

    <hr>
    <p><small>© 2024 HCL-GeoSense AI | Developed by Team Indriyaan | Powered by HCLTech</small></p>
    </body>
    </html>
    """
    
    # Set up the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(email_body, 'html'))
    
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail SMTP server
        server.starttls()
        server.login(from_email, password)
        
        # Send email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        # Informing success in Streamlit
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Chatbot Interface
def chatbot(model):
    
    st.title("HCL-GeoSense AI")
    st.write("This application predicts the likelihood of a disaster occurring based on input parameters and also provides real-time weather updates.")

    # Get input from the user
    temp = st.number_input("Enter Temperature (°C):", min_value=-100, max_value=60, value=25)
    humidity = st.number_input("Enter Humidity (%):", min_value=0, max_value=100, value=60)
    wind_speed = st.number_input("Enter Wind Speed (km/h):", min_value=0, max_value=300, value=10)
    rainfall = st.number_input("Enter Rainfall (mm):", min_value=0, max_value=100, value=5)

    disaster_event = st.selectbox("Select Disaster Event:", ['Cyclone', 'Flood', 'Heatwave', 'Tornado', 'Wildfire', 'Hurricane'])
    location = st.text_input("Enter Location (City, State):")
    date = st.date_input("Enter Date:", min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 26))

    # User email input
    email = st.text_input("Enter your email address:")

    # Convert date to string for prediction (you can use it in your model if you want to incorporate date)
    date_str = date.strftime('%Y-%m-%d')

    # User input summary
    data_summary = (f"Temperature: {temp}°C\n"
                    f"Humidity: {humidity}%\n"
                    f"Wind Speed: {wind_speed} km/h\n"
                    f"Rainfall: {rainfall} mm\n"
                    f"Disaster Event: {disaster_event}\n"
                    f"Location: {location}\n"
                    f"Date: {date_str}\n")

    # Predict and fetch current weather
    if st.button("Predict"):
        if email and location:
            # Fetch current weather conditions
            current_weather = fetch_current_weather(location)

            if current_weather:
                # Prepare weather data to be displayed in table format
                weather_data = {
                    "Temperature (°C)": [current_weather['temperature']],
                    "Humidity (%)": [current_weather['humidity']],
                    "Wind Speed (km/h)": [current_weather['wind_speed']],
                    "Cloud Description": [current_weather['cloud_description']],
                    "Rain Chances": [current_weather['rain_chances']],
                }

                weather_df = pd.DataFrame(weather_data)

                st.write("**Current Weather Conditions:**")
                st.table(weather_df)

                # Use the ML model to predict severity
                input_data = np.array([[temp, humidity, wind_speed, rainfall]])
                prediction = model.predict(input_data)
                prediction_result = prediction[0]

                # Ensure prediction results match the desired categories
                if prediction_result == "Low" and disaster_event == "Cyclone":
                    st.warning("Low severity prediction for cyclone detected. Please review the data.")
                    prediction_result = "Moderate"  # Optionally modify to avoid "Low" prediction for Cyclone

                # Prepare prediction data for table
                prediction_data = {
                    "Disaster Event": [disaster_event],
                    "Predicted Severity": [prediction_result],
                }

                prediction_df = pd.DataFrame(prediction_data)

                st.write("**Disaster Severity Prediction:**")
                st.table(prediction_df)

                # Send email with results
                send_email(email, disaster_event, prediction_result, data_summary, current_weather)

            else:
                st.error("Failed to fetch current weather conditions.")
        else:
            st.error("Please enter both your email and location.")

# Main function to execute
def main():
    # Load and preprocess dataset
    df = pd.read_csv('C:/Users/Admin/Downloads/m1/n6.csv')
    if 'Temp' in df.columns and 'Humidity' in df.columns and 'Wind_Speed' in df.columns and 'Rainfall' in df.columns and 'Target' in df.columns:
        X = df[['Temp', 'Humidity', 'Wind_Speed', 'Rainfall']]
        y = df['Target']

        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Run the chatbot interface
        chatbot(model)

if __name__ == "__main__":
    main()