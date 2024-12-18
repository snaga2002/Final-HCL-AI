import streamlit as st

def main():
    # Sidebar dropdown for selecting an option
    st.sidebar.title("Select Functionality")
    selected = st.sidebar.selectbox("Choose an Option", ["Query Assistant", "Prediction Assistant"])

    # Page navigation based on selected option
    if selected == "Query Assistant":
        try:
            # Import AI Chatbot module and execute its main function
            import query_assistant  # Ensure 'query_assistant.py' exists in your environment
            if hasattr(query_assistant, 'main'):
                query_assistant.main()  # Call 'main()' in query_assistant.py
            else:
                st.error("The 'Query Assistant' module does not have a 'main' function. Please check your module.")
        except ModuleNotFoundError:
            st.error("The 'Query Assistant' module is missing. Please check your environment.")
        except AttributeError:
            st.error("The 'Query Assistant' module does not have the required function. Please check your module.")

    elif selected == "Prediction Assistant":
        try:
            # Import AI Prediction Assistant module and execute its main function
            import prediction_assistant  # Ensure 'prediction_assistant.py' exists in your environment
            if hasattr(prediction_assistant, 'main'):
                prediction_assistant.main()  # Call 'main()' in prediction_assistant.py
            else:
                st.error("The 'Prediction Assistant' module does not have a 'main' function. Please check your module.")
        except ModuleNotFoundError:
            st.error("The 'Prediction Assistant' module is missing. Please check your environment.")
        except AttributeError:
            st.error("The 'Prediction Assistant' module does not have the required function. Please check your module.")

    
if __name__ == "__main__":
    main()