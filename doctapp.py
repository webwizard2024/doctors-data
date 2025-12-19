import streamlit as st
import os
import shutil
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# ================= CONFIGURATION =================
# CHANGE: Define two paths for the database.
# DB_REPO_PATH is where your file is in the repository.
DB_REPO_PATH = "doctors.db"
# DB_PERSISTENT_PATH is a permanent storage location on Streamlit Cloud.
DB_PERSISTENT_PATH = "/mount/data/doctors.db"

GEMINI_MODEL = "gemini-2.5-flash"

# CHANGE: Load the API key from Streamlit's secrets management.
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("API Key not found. Please configure it in your app's secrets.")
    st.stop()

# CHANGE: This block copies your database to the persistent directory.
# This only needs to run once after the app is deployed.
if not os.path.exists(DB_PERSISTENT_PATH):
    if os.path.exists(DB_REPO_PATH):
        st.info("Setting up database for the first time...")
        # The following line is removed to avoid the PermissionError.
        # The `/mount/data` directory should already exist on Streamlit Cloud.
        # os.makedirs(os.path.dirname(DB_PERSISTENT_PATH), exist_ok=True) 
        shutil.copy(DB_REPO_PATH, DB_PERSISTENT_PATH)
    else:
        st.error(f"Database file not found at '{DB_REPO_PATH}'. Please add it to your repository.")
        st.stop()
# =========================================

# 1️⃣ Connect to the persistent SQLite database
db = SQLDatabase.from_uri(f"sqlite:///{DB_PERSISTENT_PATH}")

# 2️⃣ Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=0
)

# 3️⃣ Create SQL Agent
agent = create_sql_agent(
    llm=llm,
    db=db,
    verbose=False,
    handle_parsing_errors=True
)

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
        if "RESOURCE_EXHAUSTED" in error_message and "Quota exceeded" in error_message:
            st.error("⏱️ You've hit the API's rate limit. Please wait a moment and try again.")
        else:
            st.error(f"❌ An unexpected error occurred: {e}")

st.markdown("---")
st.write("This application uses a Gemini LLM to interact with a SQLite database.")