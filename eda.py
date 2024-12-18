import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

# Load the dataset function
def load_data():
    # Load the dataset (example: from a CSV file)
    df = pd.read_csv("n6.csv")  # Replace with your actual file path or dataset source
    return df

# Define the main function for EDA
def main():
    # Load the data
    df = load_data()

    # Set up the title and description for the EDA page
    st.title("Exploratory Data Analysis - HCL-GeoSense AI")
    st.write("""
    Exploratory Data Analysis (EDA) is an approach to analyze datasets using statistical graphics, plots, and information tables.
    It is an essential part of the data analysis process as it helps to summarize their main characteristics, often visualizing them in a graphical way.
    """)

    # Display the dataset preview
    st.write("Dataset Preview:")
    st.write(df.head())

    # Create three equal columns for displaying plots
    cols = st.columns(3)

    # Scatter Plot
    with cols[0]:
        st.write("### Scatter Plot")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(df['Temp'], df['Wind_Speed'], color='blue')  # Ensure these columns exist in your DataFrame
        ax.set_title('Scatter Plot: Temp vs Wind Speed')
        ax.set_xlabel('Temperature')
        ax.set_ylabel('Wind Speed')
        st.pyplot(fig)

    # Pie Chart (assuming a categorical column, e.g., 'Target')
    with cols[1]:
        st.write("### Pie Chart")
        fig, ax = plt.subplots(figsize=(7, 7))
        pie_data = df['Target'].value_counts()  # Ensure 'Target' is a categorical column
        ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Pie Chart: Target Categories')
        st.pyplot(fig)

    # Histogram (assuming 'Temp' column exists)
    with cols[2]:
        st.write("### Histogram")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(df['Temp'], bins=10, color='green', edgecolor='black')
        ax.set_title('Histogram: Temperature Distribution')
        ax.set_xlabel('Temperature')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)

    # Box Plot for 'Humidity' (assuming 'Humidity' column exists)
    with cols[0]:
        st.write("### Box Plot")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x=df['Humidity'], color='purple', ax=ax)  # Ensure 'Humidity' exists in the DataFrame
        ax.set_title('Box Plot: Humidity Distribution')
        st.pyplot(fig)

    # Line Graph (assuming 'Date & Time' column exists for time series data)
    with cols[1]:
        st.write("### Line Graph")
        df['Date'] = pd.to_datetime(df['Date & Time'], errors='coerce')  # Ensure the 'Date & Time' column exists
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df['Date'], df['Temp'], marker='o', linestyle='-', color='orange')
        ax.set_title('Line Graph: Temperature over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature')
        st.pyplot(fig)

    # Heatmap (correlation matrix for numeric columns)
    with cols[2]:
        st.write("### Heatmap")
        numeric_df = df.select_dtypes(include=['float64', 'int64'])  # Select numeric columns
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
            ax.set_title('Heatmap: Correlation Matrix')
            st.pyplot(fig)
        else:
            st.warning("No numeric data found in the dataset for correlation analysis.")

# Run the main function
if __name__ == "__main__":
    main()
