import streamlit as st
import requests
import nltk
from nltk.tokenize import TreebankWordTokenizer
import csv
from newsapi import NewsApiClient
import pyttsx3
import threading
import speech_recognition as sr
import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from PIL import Image
import os

# Set up API keys
NEWS_API_KEY = "62b31be220434ba4939efa2bc19fe606"  # Replace with your NewsAPI key
WEATHER_API_KEY = "XO188XoLwfJDR9mNkgCdzWHU0U0RM1Zz"  # Replace with your Tomorrow.io API key

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# Load BERT model and tokenizer from Hugging Face
model_name = "bert-base-uncased"  # You can use any pre-trained BERT model
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Load your CSV file (image_name, description, category)
CSV_FILE = r"C:/Users/Admin/Downloads/m1/im_dataset.csv"
df = pd.read_csv(CSV_FILE)

# Directory containing your images
IMAGE_DIR = "C:/Users/Admin/Downloads/m1/images"

# Function to handle text-to-speech in a separate thread
def speak_text(text):
    def run_tts():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    tts_thread = threading.Thread(target=run_tts)
    tts_thread.start()

# Preprocessing text: Remove stopwords and tokenize
def preprocess_text(text):
    nltk.download('stopwords', quiet=True)
    tokenizer = TreebankWordTokenizer()
    tokens = tokenizer.tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
    return filtered_tokens

# Function to fetch the latest news
def fetch_latest_news():
    top_headlines = newsapi.get_top_headlines(language='en')
    articles = top_headlines['articles'][:5]  # Get the top 5 news articles
    news_text = ""
    for article in articles:
        news_text += f"Title: {article['title']} URL: {article['url']} "
    return news_text if news_text else "No news available at the moment."

# Weather API function
def get_weather_forecast(location):
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={location}&apikey={WEATHER_API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'timelines' in data and 'minutely' in data['timelines']:
            minute_data = data['timelines']['minutely'][0]
            temperature = minute_data['values'].get('temperature', 'No data')
            humidity = minute_data['values'].get('humidity', 'No data')
            wind_speed = minute_data['values'].get('windSpeed', 'No data')
            cloud_cover = minute_data['values'].get('cloudCover', 'No data')

            cloud_condition = map_cloud_cover_to_condition(cloud_cover)

            weather_info = {
                'Temperature': temperature,
                'Humidity': humidity,
                'Wind Speed': wind_speed,
                'Cloud Cover': cloud_condition
            }

            return {key: str(value) for key, value in weather_info.items()}
    return None

# Map cloud cover value to condition
def map_cloud_cover_to_condition(cloud_cover):
    try:
        cloud_cover = float(cloud_cover)
        if cloud_cover == 100:
            return "Fully Cloudy - Which can often lead to rain"
        elif cloud_cover >= 75:
            return "Mostly Cloudy"
        elif cloud_cover >= 50:
            return "Partly Cloudy"
        elif cloud_cover >= 25:
            return "Scattered Clouds"
        else:
            return "Clear"
    except ValueError:
        return "Invalid data"

# Function to get answer from CSV based on user query
def get_answer_from_csv(user_query, questions, answers):
    preprocessed_query = preprocess_text(user_query)
    for i, question in enumerate(questions):
        if all(word in preprocess_text(question) for word in preprocessed_query):
            return answers[i]
    return "Sorry, I don't have an answer for that."

# Load questions and answers from CSV
def load_csv(file_path):
    questions = []
    answers = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            questions.append(row[0])
            answers.append(row[1])
    return questions, answers

# Function to get query vector using BERT
def get_query_vector(query):
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    return outputs.logits

# Function to find the best matching image
def find_best_image(query, df):
    query_vector = get_query_vector(query)
    similarities = []
    
    for _, row in df.iterrows():
        description = row["description"]
        category = row["category"]
        
        description_vector = get_query_vector(description)
        
        similarity = torch.nn.functional.cosine_similarity(query_vector, description_vector).item()
        similarities.append((similarity, row["image_name"], description, category))
    
    if not similarities:
        return None, None, None
    
    best_match = max(similarities, key=lambda x: x[0])
    return best_match[1], best_match[2], best_match[3]

# Voice-to-Text Function
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            user_voice_input = recognizer.recognize_google(audio)
            return user_voice_input
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None  # Return None for errors

# Streamlit UI for chatbot
# Refined Matching Function
def find_best_image(query, df):
    query = query.lower()  # Normalize the query to lowercase
    similarities = []

    for _, row in df.iterrows():
        description = row["description"].lower()  # Normalize descriptions to lowercase
        category = row["category"].lower()
        
        # Check if the query contains keywords from the description
        description_keywords = description.split()
        query_keywords = query.split()

        # Count how many words in the query match words in the description
        match_count = sum(1 for word in query_keywords if word in description_keywords)
        
        if match_count > 0:  # If there are any matches
            similarities.append((match_count, row["image_name"], description, category))

    # If no matches found, return None
    if not similarities:
        return None, None, None

    # Sort by the match count and select the best match
    best_match = max(similarities, key=lambda x: x[0])
    return best_match[1], best_match[2], best_match[3]

# Updated chatbot UI
def main():
    st.title("HCL-GeoSense-AI Query Assistant")
    st.write("Real-Time Weather Updates and Response Assistant")

    # Load questions and answers from CSV
    questions, answers = load_csv("csv1.csv")  # Path to your CSV file

    # User Input Section
    user_message = None
    input_container = st.container()

    with input_container:
        col1, col2 = st.columns([9, 1])  # Adjusted to have more space for the text input
        with col1:
            user_message = st.text_input("Enter your message here...", key="text_message")
        with col2:
            if st.button("🎤"):  # Microphone icon as button
                voice_input = voice_to_text()
                if voice_input:
                    user_message = voice_input

    # Handle user input
    if user_message:
        with st.spinner('Thinking...'):
            # Check if the message is asking for an image
            if "image" in user_message.lower() or "picture" in user_message.lower() or "photo" in user_message.lower():
                # Find the best matching image based on user message
                best_image_name, best_description, best_category = find_best_image(user_message, df)
                
                if best_image_name:
                    image_path = os.path.join(IMAGE_DIR, best_image_name)
                    found_image = (image_path, f"Best Match: {best_description} - Category: {best_category}")
                    bot_response = f"Here is the image you requested: {best_description}."
                else:
                    found_image = None
                    bot_response = "Sorry, I couldn't find an image for your request."
            else:
                # Default query - get answer from CSV or process weather/news query
                if "news" in user_message.lower():
                    bot_response = fetch_latest_news()
                    found_image = None
                elif "weather" in user_message.lower():
                    location = user_message.split("weather")[-1].strip()
                    weather_data = get_weather_forecast(location)
                    if weather_data:
                        bot_response = "\n".join([f"**{key}**: {value}" for key, value in weather_data.items()])
                    else:
                        bot_response = "Unable to fetch weather data for the specified location."
                    found_image = None
                else:
                    # Check CSV for answer to the query
                    bot_response = get_answer_from_csv(user_message, questions, answers)
                    found_image = None

            # Display chat response
            st.text_area("Chat", value=f"You: {user_message}\n\nBot: {bot_response}", height=300)
            
            # Display the image if found
            if found_image:
                st.image(found_image[0], caption=found_image[1])
            
            # Speak the bot's response
            speak_text(bot_response)


# Run the UI
if __name__ == "__main__":
    main()
