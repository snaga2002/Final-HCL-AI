import streamlit as st
from streamlit_option_menu import option_menu

# Set up the page layout and icon
st.set_page_config(
    page_title="HCL-GeoSense AI",  # Custom title for the app
    page_icon="hcl.png",  # Path to the app's logo
    layout="wide"
)

# Custom CSS for styling, including the background color and image
st.markdown(
    """
    <style>
    /* Apply background color and image */
    body {
        background-color: #080808;  /* Applying #080808 color */
        background-image: url('bg.png');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        margin: 0;
        padding: 0;
    }
    /* Override the default Streamlit container styles */
    .stApp {
        background-color: rgba(8, 8, 8, 0.9);  /* Semi-transparent background with RGB values (8, 8, 8) */
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    .scrolling-bar {
        background-color: rgba(0, 0, 0, 0.7); /* Semi-transparent background */
        color: #fff;
        padding: 10px;
        font-size: 16px;
        white-space: nowrap;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .scrolling-bar div {
        display: inline-block;
        animation: scroll 10s linear infinite;
    }
    @keyframes scroll {
        from {
            transform: translateX(100%);
        }
        to {
            transform: translateX(-100%);
        }
    }
    .footer {
        background-color: rgba(0, 0, 0, 0.7); /* Semi-transparent background */
        color: #fff;
        text-align: center;
        padding: 10px 0;
        box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
        font-size: 14px;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Display the logo
# Display the logo
# Display the logo with a smaller size
# Display the logo with a smaller size (e.g., 100px width)
st.image("h4.png", width=200, caption="HCL-GeoSense AI")





# Add a scrolling bar for updates with slower movement
st.markdown(
    """
    <div class="scrolling-bar">
        <div>🔥 Latest Updates: GeoSense AI wins HCL Hackathon!  |  Delhi air pollution: Quality slips to 'Severe' again; GRAP-IV measures imposed |  India faces high climate risk as 2024 threatens to breach 1.5°C threshold: WMO chief at COP29  |  🌟 Stay tuned for more updates. 🚀</div>
    </div>
    <style>
    .scrolling-bar {
        background-color: rgba(0, 0, 0, 0.7); /* Semi-transparent background */
        color: #fff;
        padding: 10px;
        font-size: 16px;
        white-space: nowrap;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        text-align: center;
    }
    .scrolling-bar div {
        display: inline-block;
        animation: scroll 20s linear infinite; /* Increased duration for slower scroll */
    }
    @keyframes scroll {
        from {
            transform: translateX(100%);
        }
        to {
            transform: translateX(-100%);
        }
    }
    </style>
    """, unsafe_allow_html=True
)

# Set up the navigation menu with icons
selected = option_menu(
    "",  # Empty string for menu_title
    options=["Home", "Prediction", "EDA", "About", "Precaution", "Login", "Admin", "HCL-GPT", "Wildfire"],
    icons=["house", "bar-chart-line", "search", "info-circle", "shield-check", "key", "bell", "chat", "fire"],
    orientation="horizontal"
)

# Page navigation based on selected option
if selected == "Home":
    try:
        import home
        home.main()
    except ModuleNotFoundError:
        st.error("The 'home' module is missing.")

elif selected == "Prediction":
    try:
        import prediction
        prediction.main()
    except ModuleNotFoundError:
        st.error("The 'prediction' module is missing.")

elif selected == "EDA":
    try:
        import eda
        eda.main()
    except ModuleNotFoundError:
        st.error("The 'EDA' module is missing.")

elif selected == "About":
    try:
        import about
        about.main()
    except ModuleNotFoundError:
        st.error("The 'about' module is missing.")

elif selected == "Precaution":
    try:
        import precaution
        precaution.main()
    except ModuleNotFoundError:
        st.error("The 'precaution' module is missing.")

elif selected == "Login":
    try:
        import login
        login.main()
    except ModuleNotFoundError:
        st.error("The 'login' module is missing.")

elif selected == "Admin":
    try:
        import admin
        admin.main()
    except ModuleNotFoundError:
        st.error("The 'admin' module is missing.")

elif selected == "HCL-GPT":
    try:
        import chatbot
        chatbot.main()  # Call the chatbot() function directly
    except ModuleNotFoundError:
        st.error("The 'chatbot' module is missing.")

elif selected == "Wildfire":
    try:
        import wildfire
        wildfire.main()  # Call the chatbot() function directly
    except ModuleNotFoundError:
        st.error("The 'chatbot' module is missing.")

# Footer
st.markdown(
    """
    <div class="footer">
        © 2024 HCL-GeoSense AI | Developed by Team Indriyaan | Powered by HCLTech
    </div>
    """, unsafe_allow_html=True
)
