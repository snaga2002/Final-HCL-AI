import re
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# Function to extract input information from user input
def extract_information(user_input):
    patterns = {
        "location": r"Location\s*=\s*([A-Za-z\s]+)",
        "date": r"Date\s*=\s*(\d{2}-\d{2}-\d{4})",
        "temp": r"Temp\s*=\s*(\d+(\.\d+)?)",
        "humidity": r"Humidity\s*=\s*(\d+)",
        "wind_speed": r"Wind\s*Speed\s*=\s*(\d+)",
        "rainfall": r"Rainfall\s*=\s*(\d+)"
    }
    
    # Extract values using regex
    extracted = {key: re.search(pattern, user_input) for key, pattern in patterns.items()}
    extracted_values = {key: (float(match.group(1)) if key in ["temp", "humidity", "wind_speed", "rainfall"] else match.group(1)) 
                        if match else None 
                        for key, match in extracted.items()}
    
    return extracted_values

# Function to train the models
def train_models(data):
    # Encode categorical data
    le_event = LabelEncoder()
    le_location = LabelEncoder()
    le_target = LabelEncoder()
    
    data['Event'] = le_event.fit_transform(data['Event'])
    data['Location'] = le_location.fit_transform(data['Location'])
    data['Target'] = le_target.fit_transform(data['Target'])
    
    # Splitting features and targets (exclude Location for target prediction)
    X = data[['Temp', 'Humidity', 'Wind_Speed', 'Rainfall']]  # No location for target prediction
    y_event = data['Event']  # Target for Event prediction
    y_target = data['Target']  # Target for Target prediction

    # Split data into training and test sets
    X_train, X_test, y_event_train, y_event_test = train_test_split(X, y_event, test_size=0.2, random_state=42)
    _, _, y_target_train, y_target_test = train_test_split(X, y_target, test_size=0.2, random_state=42)
    
    # Train models for Event and Target prediction
    model_event = RandomForestClassifier(random_state=42)
    model_event.fit(X_train, y_event_train)

    model_target = RandomForestClassifier(random_state=42)
    model_target.fit(X_train, y_target_train)

    return model_event, model_target, le_event, le_location, le_target, data

# Function to predict Event and Target
def predict_event_and_target(location, temp, humidity, wind_speed, rainfall, model_event, model_target, le_event, le_location, le_target, df):
    # Transform inputs for prediction
    location_encoded = le_location.transform([location])[0] if location in le_location.classes_ else -1
    if location_encoded == -1:
        location_encoded = 0  # Or handle as a default value (if required)

    # Use only the environmental features (exclude Location)
    input_features = [[temp, humidity, wind_speed, rainfall]]  # No location for target prediction

    # Predict Event
    predicted_event_encoded = model_event.predict(input_features)[0]
    predicted_event = le_event.inverse_transform([predicted_event_encoded])[0]

    # Predict Target (without location)
    predicted_target_encoded = model_target.predict(input_features)[0]
    predicted_target = le_target.inverse_transform([predicted_target_encoded])[0]

    return predicted_event, predicted_target

# Precautionary descriptions based on Event and Target
def get_precautionary_description(event, target):
    precautions = {
        "Flood": {
            "Red": "Evacuate immediately to higher ground. Avoid low-lying areas and stay indoors until the all-clear is given.",
            "Orange": "Prepare for potential flooding. Ensure drainage systems are clear, and stock up on necessary supplies.",
            "Yellow": "Monitor local authorities' updates. Prepare for possible floods by moving valuable items to higher ground."
        },
        "Tornado": {
            "Red": "Take immediate shelter in a basement or storm cellar. Stay away from windows and cover your head.",
            "Orange": "Move to an interior room on the lowest floor. Avoid large open areas and stay away from windows.",
            "Yellow": "Monitor weather reports and be ready to take shelter if necessary. Secure outdoor objects."
        },
        "Earthquake": {
            "Red": "Drop to the ground, cover your head and neck, and take shelter under a sturdy piece of furniture. Stay inside until it's safe.",
            "Orange": "Drop, cover, and hold on. If outside, move away from buildings, trees, and power lines.",
            "Yellow": "Be prepared for aftershocks. Secure heavy objects and stay alert for official updates."
        },
        "Hurricane": {
            "Red": "Evacuate if instructed by authorities. Secure windows and doors. Stock up on emergency supplies.",
            "Orange": "Prepare for the storm. Secure outdoor objects and check for potential flooding risks.",
            "Yellow": "Monitor weather reports and begin securing outdoor items. Ensure an emergency kit is ready."
        },
        "Wildfire": {
            "Red": "Evacuate immediately if instructed. Avoid using vehicles near the fire. Stay away from smoke and flames.",
            "Orange": "Prepare for evacuation. Keep a go-bag ready and stay alert for changing fire conditions.",
            "Yellow": "Be ready to evacuate if conditions worsen. Clear debris around your home to reduce fire risk."
        },
        "Cyclone": {
            "Red": "Evacuate immediately to a safe, sturdy shelter. Stay away from windows and cover yourself with a heavy object.",
            "Orange": "Secure your home, especially windows and doors. Gather emergency supplies and stay indoors.",
            "Yellow": "Monitor local weather updates. Prepare your house by reinforcing windows and checking for debris."
        },
        "Heatwave": {
            "Red": "Avoid going outside during peak heat. Drink plenty of water and stay in air-conditioned spaces if possible.",
            "Orange": "Limit outdoor activity to cooler parts of the day. Wear light clothing and drink water frequently.",
            "Yellow": "Stay informed about temperature changes. Ensure proper hydration and wear protective clothing."
        }
    }
    
    # Return the precautionary message based on event and target
    return precautions.get(event, {}).get(target, "No specific precautions available for this combination.")

# Streamlit main application
def main():
    st.title("HCL-GeoSense-AI Prediction Assistant")

    st.write("Type your input to make a prediction (e.g., 'Make prediction for Location = Chennai, Date = 30-11-2024, Temp = 28.5, Humidity = 85, Wind Speed = 120, Rainfall = 35').")
    user_input = st.text_input("Enter your request here:")

    if user_input:
        # Extract data from user input
        try:
            extracted_values = extract_information(user_input)
            location = extracted_values['location']
            date = extracted_values['date']
            temp = extracted_values['temp']
            humidity = extracted_values['humidity']
            wind_speed = extracted_values['wind_speed']
            rainfall = extracted_values['rainfall']

            if None in extracted_values.values():
                st.error("Invalid input. Please ensure all fields (Location, Date, Temp, Humidity, Wind Speed, Rainfall) are provided.")
            else:
                # Load dataset
                # Replace with your dataset path
                dataset_path = "C:/Users/Admin/Downloads/m1/n6.csv"
                df = pd.read_csv(dataset_path)

                # Train the models
                model_event, model_target, le_event, le_location, le_target, df_encoded = train_models(df)

                # Make prediction
                predicted_event, predicted_target = predict_event_and_target(location, temp, humidity, wind_speed, rainfall, model_event, model_target, le_event, le_location, le_target, df_encoded)

                # Display results
                st.success(f"Predicted Event: {predicted_event}")
                st.success(f"Predicted Target: {predicted_target}")
                
                # Get and display precautionary description
                precaution_description = get_precautionary_description(predicted_event, predicted_target)
                st.write(f"**Precautionary Measures:** {precaution_description}")
        
        except ValueError as e:
            st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
