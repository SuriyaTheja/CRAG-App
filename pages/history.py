import streamlit as st
import pandas as pd
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="Query History",
    page_icon="🗂️",
    layout="wide"
)

# --- Background Image and Styling (Same as Home) ---
def set_styles():
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: black;
        background-size: cover;
        background-attachment: fixed;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: black;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgb(50, 100, 200);
    }}
    /* Make Dataframe headers stand out */
    .stDataFrame th {{
        background-color: #f0f2f6;
        color: #333;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

set_styles()

# --- Page Protection ---
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in from the `1_Home` page to view history.")
    st.stop()

# --- History Page Content ---
st.title("🗂️ Session Query History")

if "history" in st.session_state and st.session_state.history:
    st.markdown("Here are all the questions and answers from your current session.")
    
    # Convert history list of dicts to a DataFrame
    df = pd.DataFrame(st.session_state.history)
    
    # Display the DataFrame
    st.dataframe(df, use_container_width=True)
    
    # --- Download Button ---
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_df_to_csv(df)
    
    st.download_button(
        label="Download History as CSV",
        data=csv_data,
        file_name="crag_chat_history.csv",
        mime="text/csv",
        type="primary"
    )
    
else:
    st.info("No queries have been made in this session. Go to the `2_CRAG_App` page to start.")