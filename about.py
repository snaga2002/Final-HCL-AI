import streamlit as st

def main():
    st.title("HCL-GeoSense AI")
    st.write(
        """
        **HCL-GeoSense AI** is a powerful web application designed to monitor, visualize, and analyze disaster events in real-time.
        By leveraging AI-driven data extraction from news articles and various data sources,
        HCL-GeoSense AI provides an interactive platform for understanding both ongoing and historical disaster occurrences 
        across different regions.
        """
    )

    st.subheader("Key Features")
    st.markdown("""
    1. **Interactive Disaster Map**: Explore disaster events geographically with an interactive map powered by Folium.
    2. **Filter by Type and Date**: Refine disaster data using event type and date range filters in the sidebar.
    3. **Insights & Analytics**: Dive into dynamic analytics, including charts, word clouds, and event timelines.
    4. **Real-Time Event Marquee**: See recent key events scrolling in the sidebar, each linked to detailed sources.
    5. **Continuous Updates**: Visualizations and data refresh automatically based on selected filters for a real-time experience.
    6. **Interactive AI Chatbot**: AI Assistant with real-time weather forecasts and interactive responses.
    """)

    st.subheader("Data Sources")
    st.write(
        """
        HCL-GeoSense AI gathers data from NewsAPI to access real-time news articles related to disaster events.
        """
    )

    st.subheader("Technologies")
    st.write(
        """
        - **Python**: Core language for data processing, visualization, and backend logic.
        - **Streamlit**: Framework for creating interactive and user-friendly web applications.
        - **Pandas**: Used for data manipulation and transformation.
        - **Folium**: Enables the creation of interactive geospatial visualizations.
        - **Plotly**: For generating interactive and insightful charts.
        - **Natural Language Processing (NLP)**: Extracts and processes disaster-related information from news articles.
        - **Machine Learning Models**: Used to classify and categorize disaster types based on text data.
        - **Deep Learning**: Enhances data extraction and pattern recognition within large volumes of unstructured data.
        - **GeoAI**: Integrates geospatial data with AI for improved disaster detection and monitoring.
        - **SMTP**: Used for sending email notifications and alerts related to disaster events.
        """
    )

if __name__ == "__main__":
    main()
