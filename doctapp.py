import streamlit as st
import os
import sys
import sqlite3
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# ================= CONFIGURATION =================
# This path is for deployment on Streamlit Community Cloud.
# It ensures the database file persists across app restarts.
DB_PATH = "/mount/data/doctors.db"

# Use the correct and more efficient model name.
GEMINI_MODEL = "gemini-1.5-flash"

# --- Securely load API key from Streamlit secrets ---
# This will work on Streamlit Community Cloud and locally if you have a .streamlit/secrets.toml file.
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("Failed to load GOOGLE_API_KEY from secrets. Please configure it in your deployment settings or local `.streamlit/secrets.toml` file.")
    st.stop()
# =========================================

# --- One-time Database Setup for Deployment ---
# This function creates the database and populates it if it doesn't already exist.
# This is crucial for deployment platforms where the file system might be empty initially.
def setup_database():
    """Creates the database and populates it with sample data if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        st.info("Database not found. Creating and populating a new one...")
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Sample data for the dermatologists table
        dermatologists_data = [
            (1, 'Dr. Alice Smith', 'New York', 'Active', 'Acne, Eczema'),
            (2, 'Dr. Bob Johnson', 'Los Angeles', 'Active', 'Psoriasis, Skin Cancer'),
            (3, 'Dr. Carol Williams', 'Chicago', 'Inactive', 'Rosacea'),
            (4, 'Dr. David Brown', 'Houston', 'Active', 'Dermatitis, Allergies'),
        ]

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE dermatologists (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    status TEXT NOT NULL,
                    specialties TEXT
                )
            ''')
            cursor.executemany('''
                INSERT INTO dermatologists (id, name, city, status, specialties)
                VALUES (?, ?, ?, ?, ?)
            ''', dermatologists_data)
            conn.commit()
            conn.close()
            st.success("Database setup complete.")
        except sqlite3.Error as e:
            st.error(f"An error occurred during database setup: {e}")
            st.stop()

# Run the setup function
setup_database()

# 1️⃣ Connect to SQLite database
try:
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
except Exception as e:
    st.error(f"Could not connect to the database at {DB_PATH}. Error: {e}")
    st.stop()

# 2️⃣ Initialize Gemini LLM
try:
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=0
    )
except Exception as e:
    st.error(f"Failed to initialize the Language Model. Check your API key and model name. Error: {e}")
    st.stop()

# 3️⃣ Create SQL Agent with error handling
try:
    agent = create_sql_agent(
        llm=llm,
        db=db,
        verbose=True,  # Set to False in production to hide logs
        handle_parsing_errors=True
    )
except Exception as e:
    st.error(f"Failed to create the SQL Agent. Error: {e}")
    st.stop()

# 4️⃣ Streamlit UI
st.set_page_config(page_title="Dermatologist SQL Agent", page_icon="🩺")
st.title("🩺 Gemini SQL RAG Agent for Doctors DB")
st.write("Ask questions about dermatologists in the database. For example: 'Show all active dermatologists in New York'.")

# Input box
user_query = st.text_input("Your Question:")

if user_query:
    try:
        with st.spinner("Generating answer..."):
            response = agent.run(user_query)
        st.subheader("🤖 Answer:")
        st.write(response)
    except Exception as e:
        error_message = str(e)
        # Provide a user-friendly message for rate limiting
        if "RESOURCE_EXHAUSTED" in error_message and "Quota exceeded" in error_message:
            st.error("⏱️ You've hit the API's rate limit. Please wait a moment and try again.")
        else:
            st.error(f"❌ An unexpected error occurred: {e}")

st.markdown("---")
st.write("This application uses a Gemini LLM to interact with a SQLite database.")