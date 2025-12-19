import streamlit as st
import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# ================= CONFIGURATION =================
# The database file is expected to be in the same directory as the app.
DB_PATH = "doctors.db"
GEMINI_MODEL = "gemini-2.5-flash"

# Load the API key from Streamlit's secrets management
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("API Key not found. Please configure it in your app's secrets.")
    st.stop()
# =========================================

# 1️⃣ Connect directly to the database file in the repository
# NOTE: This may fail if the environment is read-only.
try:
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    st.success("✅ Successfully connected to the database.")
except Exception as e:
    st.error(f"❌ Error: Could not connect to the database at '{DB_PATH}'. Please ensure 'doctors.db' is in your repository. Error: {e}")
    st.stop()

# 2️⃣ Initialize Gemini LLM
try:
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0)
except Exception as e:
    st.error(f"Failed to initialize the Language Model. Check your API key and model name. Error: {e}")
    st.stop()

# 3️⃣ Create SQL Agent
try:
    agent = create_sql_agent(llm=llm, db=db, verbose=False, handle_parsing_errors=True)
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
        if "RESOURCE_EXHAUSTED" in error_message and "Quota exceeded" in error_message:
            st.error("⏱️ You've hit the API's rate limit. Please wait a moment and try again.")
        else:
            st.error(f"❌ An unexpected error occurred: {e}")

st.markdown("---")
st.write("This application uses a Gemini LLM to interact with a SQLite database.")