import streamlit as st
import requests
from datetime import datetime
import folium
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from folium import Icon

# News API Key and URL
API_KEY = "62b31be220434ba4939efa2bc19fe606"  # Replace with your actual API key
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Function to fetch news articles
def fetch_news(start_date, end_date):
    query = "disaster"
    params = {
        'q': query,
        'from': start_date,
        'to': end_date,
        'apiKey': API_KEY,
        'language': 'en'
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        return response.json()['articles']
    else:
        st.error("Error fetching news")
        return []

# Function to display news in the sidebar with a scrolling effect
def display_news(news_articles):
    if news_articles:
        st.sidebar.subheader("Recent News")

        # Create a string with the HTML for the news links
        marquee_content = ""
        for article in news_articles:
            marquee_content += f"<a href='{article['url']}' target='_blank'>{article['title']}</a><br><br>"

        # Add CSS for marquee (slower scrolling)
        marquee_html = f"""
            <div class="marquee-container">
                <div class="marquee-content">{marquee_content}</div>
            </div>
            <style>
                .marquee-container {{
                    height: 100%; /* Set the height to occupy the entire sidebar */
                    overflow: hidden;
                }}
                .marquee-content {{
                    animation: marquee 60s linear infinite; /* Slower scrolling */
                    padding-top: 10px;
                }}
                @keyframes marquee {{
                    0%   {{ transform: translateY(100%); }}
                    100% {{ transform: translateY(-100%); }}
                }}
                .marquee-content:hover {{
                    animation-play-state: paused;
                }}
            </style>
        """

        # Display the scrolling news in the sidebar
        st.sidebar.markdown(marquee_html, unsafe_allow_html=True)
    else:
        st.sidebar.subheader("No recent news available.")

# Function to display disaster data on a map (filtered for India)
def display_disasters_on_map(filtered_df):
    disaster_map = folium.Map(location=[20, 80], zoom_start=5)  # Centered over India

    # Create a marker cluster
    marker_cluster = MarkerCluster().add_to(disaster_map)

    # Loop through the filtered dataframe to add markers for disaster events
    for index, row in filtered_df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<a href='{row['url']}' target='_blank'>{row['title']}</a>",
            tooltip=f"{row['disaster_event']}, {row['Location']}",
            icon=Icon(color='red', icon='info-sign')  # Red color icon
        ).add_to(marker_cluster)

    # Display the Folium map in Streamlit
    st_folium(disaster_map, width=1000, height=500)

def main():
    # Sidebar for date range input
    st.sidebar.header("Filter Data")
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 12, 2))
    end_date = st.sidebar.date_input("End Date", datetime(2024, 12, 15))
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Fetch news based on date range
    with st.spinner('Fetching news articles...'):
        news_articles = fetch_news(start_date_str, end_date_str)

    # Display news in the sidebar with scrolling effect
    display_news(news_articles)

    # Example filtered dataframe
    filtered_df = pd.DataFrame({
        'Latitude': [13.0827, 16.5062, 28.6139, 11.6854, 18.3030, 13.0827],
        'Longitude': [80.2707, 80.6480, 77.2090, 76.1320, 80.1514, 80.2707],
        'url': [
            'https://example.com/1',
            'https://example.com/2',
            'https://example.com/3',
            'https://example.com/4',
            'https://example.com/5',
            'https://example.com/6'
        ],
        'title': [
            'Flood in Chennai',
            'Flood in Vijayawada',
            'Air pollution in Delhi',
            'Flood in Wayanad',
            'Tornado in Medaram',
            'Bengal cyclone in Chennai'
        ],
        'disaster_event': ['Flood', 'Flood', 'Pollution', 'Flood', 'Tornado', 'Cyclone'],
        'Location': [
            'Chennai',
            'Vijayawada',
            'Delhi',
            'Wayanad',
            'Medaram',
            'Chennai'
        ]
    })

    # Display disasters on the map
    display_disasters_on_map(filtered_df)

if __name__ == "__main__":
    main()
