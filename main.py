import os
import streamlit as st
import pyrebase  # Added for Firebase
import json      # Added to parse Firebase errors
from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")
# --- Firebase Configuration (USER MUST FILL THIS) ---
# 1. Go to your Firebase project settings
# 2. Go to "Project settings" > "General"
# 3. Scroll down to "Your apps" and select or create a Web app (</>).
# 4. Find the `firebaseConfig` object and copy/paste its contents here.
# 5. IMPORTANT: In Firebase Console > Authentication > Sign-in method, ENABLE "Email/Password"
#
# 6. !! PYTHON SYNTAX WARNING !!
#    When you paste your config from Firebase, it might include a line with
#    a JavaScript comment (like `// ...` for `measurementId`).
#    Python does NOT allow `//` comments. You MUST change `//` to `#`
#    or delete that comment line entirely.
#
#    BAD (causes SyntaxError):
#    "measurementId": "G-..." // For Firebase JS SDK v7.20.0...
#
#    GOOD (Python-safe):
#    "measurementId": "G-..." # For Firebase JS SDK v7.20.0...
#
firebase_config = {
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "projectId": os.getenv("PROJECT_ID"),
  "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
  "storageBucket": os.getenv("STORAGE_BUCKET"),
  "appId": os.getenv("APP_ID"),
  "measurementId": os.getenv("MEASUREMENT_ID"), # For Firebase JS SDK v7.20.0 and later, measurementId is optional

  # --- FIX ADDED HERE ---
  # Pyrebase requires the databaseURL, even if only using Auth.
  # This is typically your projectID + "-default-rtdb.firebaseio.com"
  "databaseURL": os.getenv("DATABASE_URL")
}

# --- Initialize Firebase ---
@st.cache_resource
def init_firebase():
    """Initializes and returns the Firebase Auth object."""
    try:
        # Check if all required config keys are filled
        if not all(firebase_config.get(key) not in [None, "", "YOUR_API_KEY"] for key in ["apiKey", "authDomain", "projectId"]):
            st.error("Firebase configuration is incomplete. Please fill in `firebase_config` in main.py.")
            return None
        firebase = pyrebase.initialize_app(firebase_config)
        return firebase.auth()
    except Exception as e:
        # This can happen if config is malformed
        st.error(f"Failed to initialize Firebase: {e}")
        return None

auth = init_firebase()

# --- Page Configuration ---
st.set_page_config(
    page_title="CRAG Home",
    page_icon="🏠",
    layout="centered"
)

# --- Background Color and Styling ---
def set_styles():
    st.markdown(f"""
    <style>
    /* Main app background: CHANGED TO SOLID BLACK */
    .stApp {{
        background-color: black; 
    }}
    
    /* Content blocks (login, text, etc.) */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: rgb(50, 100, 200);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgb(0, 51, 102);
    }}
    
    /* Big 'CRAG' Title */
    .crag-title {{
        font-size: 8rem;
        font-weight: 900;
        text-align: center;
        color: #f0f0f0;
    }}
    
    /* Subtitle */
    .crag-subtitle {{
        font-size: 1.5rem;
        font-weight: 300;
        text-align: center;
        color: #ddd;
    }}
    
    body, p, h1, h2, h3, h4, .st-bh {{
        color: #f0f0f0; /* Light gray for contrast on black */
    }}
    </style>
    """, unsafe_allow_html=True)

set_styles()

# --- Initialize Session State ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None  # To store user info

# --- Login Logic (REPLACED with Firebase) ---
def login_form():
    """Displays the Firebase Login/Sign Up form."""
    st.markdown("<h1 style='text-align: center;'>Login to CRAG</h1>", unsafe_allow_html=True)
    
    if auth is None:
        st.warning("Firebase is not initialized. Please check your `firebase_config`.")
        return

    # A toggle to switch between Login and Sign Up
    action = st.radio("Choose action:", ("Login", "Sign Up"), horizontal=True, label_visibility="collapsed")

    with st.form("firebase_auth_form"):
        email = st.text_input("Email", placeholder="user@example.com")
        password = st.text_input("Password", type="password", placeholder="********")
        submitted = st.form_submit_button(action)

        if submitted:
            try:
                if action == "Login":
                    # Try to sign in the user
                    user = auth.sign_in_with_email_and_password(email, password)
                    st.session_state.authenticated = True
                    st.session_state.user = user  # Store user details
                    st.rerun()
                
                elif action == "Sign Up":
                    # Try to create a new user
                    user = auth.create_user_with_email_and_password(email, password)
                    st.session_state.authenticated = True
                    st.session_state.user = user  # Store user details
                    st.success("Account created successfully! You are now logged in.")
                    st.balloons()
                    st.rerun()

            except Exception as e:
                # Firebase errors are often nested in a JSON string.
                try:
                    # Try to parse the specific Firebase error message
                    error_data = e.args[1]
                    error_json = json.loads(error_data)
                    error_message = error_json.get('error', {}).get('message', '')
                    
                    if error_message in ["EMAIL_NOT_FOUND", "INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"]:
                        st.error("Invalid email or password. Please try again.")
                    elif error_message == "EMAIL_EXISTS":
                        st.error("An account with this email already exists. Please switch to Login.")
                    elif error_message == "WEAK_PASSWORD":
                        st.error("Password is too weak. It must be at least 6 characters.")
                    elif error_message == "OPERATION_NOT_ALLOWED":
                        st.error("Email/Password sign-in is disabled in your Firebase console. Go to Firebase Console > Authentication > Sign-in method, and enable 'Email/Password'.")
                    elif error_message == "TOO_MANY_ATTEMPTS_TRY_LATER":
                        st.error("Too many failed attempts. Please try again later.")
                    else:
                        st.error(f"Firebase error: {error_message}")
                except (IndexError, KeyError, json.JSONDecodeError, AttributeError):
                    # Check for network/DNS connection errors
                    err_str = str(e)
                    if "getaddrinfo failed" in err_str or "11001" in err_str:
                        st.error("🌐 **Network / DNS Error:** Unable to connect to Google Firebase (`www.googleapis.com`).\n\n"
                                 "• Please check your internet connection.\n"
                                 "• If you are using a VPN, proxy, or firewall, try temporarily disabling it.\n"
                                 "• Try flushing DNS: Run `ipconfig /flushdns` in Command Prompt.\n"
                                 "• Try switching your DNS to Google DNS (8.8.8.8) or Cloudflare (1.1.1.1).")
                    elif "Max retries exceeded" in err_str:
                        st.error("🌐 **Connection Timeout:** Could not reach Firebase servers. Please verify your internet connection.")
                    else:
                        st.error(f"An error occurred: {e}")

# --- Main Page Content ---
if not st.session_state.authenticated:
    login_form()
else:
    # --- Home Page Content (when logged in) ---
    st.markdown("<p class='crag-title'>CRAG</p>", unsafe_allow_html=True)
    st.markdown("<p class='crag-subtitle'>Contextual Retrieval-Augmented Generation</p>", unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to your personal document analysis tool.
    
    This application allows you to 'chat' with your PDF documents using a powerful Retrieval-Augmented Generation (RAG) system.
    
    ### How to Use:
    1.  **Go to the `2_CRAG_App` page** using the sidebar on the left.
    2.  **Upload your PDF** in the sidebar.
    3.  **Wait for it to be processed.** A success message will appear.
4.  **Start chatting!** Ask any question about the document in the chat box.
    5.  **Check the `3_History` page** to see all your questions and answers.
    """)
    
    # Display the user's email if available
    if st.session_state.user and 'email' in st.session_state.user:
         st.sidebar.success(f"Logged in as: {st.session_state.user['email']}")

    if st.button("Logout", type="primary"):
        st.session_state.authenticated = False
        st.session_state.user = None  # Clear user info
        st.rerun()

