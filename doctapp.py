import streamlit as st
import os
import shutil
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import os
import shutil
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# ================= CONFIGURATION =================
DB_REPO_PATH = "doctors.db"
DB_PERSISTENT_PATH = "/mount/data/doctors.db"
GEMINI_MODEL = "gemini-2.5-flash"

# Load the API key from Streamlit's secrets management
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("API Key not found. Please configure it in your app's secrets.")
    st.stop()

# --- Final attempt at database setup with detailed checks ---
def setup_database():
    st.write("🔍 Checking database setup...")
    
    # Check if the persistent database already exists
    if os.path.exists(DB_PERSISTENT_PATH):
        st.write("✅ Persistent database already exists.")
        return

    # If not, check if the source file exists in the repo
    if not os.path.exists(DB_REPO_PATH):
        st.error(f"❌ Error: The source database file '{DB_REPO_PATH}' was not found in your repository.")
        st.stop()
    
    st.write(f"✅ Source database '{DB_REPO_PATH}' found.")

    # Check if the parent directory exists and is writable
    parent_dir = os.path.dirname(DB_PERSISTENT_PATH)
    st.write(f"🔍 Checking if directory '{parent_dir}' is accessible...")
    
    if not os.path.exists(parent_dir):
        st.error(f"❌ Error: The persistent storage directory '{parent_dir}' does not exist. This is a platform configuration issue.")
        st.stop()

    if not os.access(parent_dir, os.W_OK):
        st.error(f"❌ Error: The application does not have permission to write to the directory '{parent_dir}'. This is a platform configuration issue.")
        st.stop()

    st.write(f"✅ Directory '{parent_dir}' is accessible. Attempting to copy...")
    
    # Attempt to copy the file
    try:
        shutil.copy(DB_REPO_PATH, DB_PERSISTENT_PATH)
        st.write("✅ Database successfully copied to persistent storage.")
    except Exception as e:
        st.error(f"❌ Error: Failed to copy the database. The server reported an error: {e}")
        st.stop()

# Run the setup function
setup_database()
# =========================================

# 1️⃣ Connect to the persistent SQLite database
try:
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PERSISTENT_PATH}")
    st.write("✅ Successfully connected to the database.")
except Exception as e:
    st.error(f"❌ Error: Could not connect to the database at {DB_PERSISTENT_PATH}. Error: {e}")
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
# ================= CONFIGURATION =================
DB_REPO_PATH = "doctors.db"
DB_PERSISTENT_PATH = "/mount/data/doctors.db"
GEMINI_MODEL = "gemini-2.5-flash"

# Load the API key from Streamlit's secrets management
try:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception as e:
    st.error("API Key not found. Please configure it in your app's secrets.")
    st.stop()

# --- A more robust setup function with better error reporting ---
def setup_database():
    st.write("🔍 Checking database setup...")
    # Check if the persistent database already exists
    if os.path.exists(DB_PERSISTENT_PATH):
        st.write("✅ Persistent database already exists.")
        return

    # If not, check if the source file exists in the repo
    if not os.path.exists(DB_REPO_PATH):
        st.error(f"❌ Error: The source database file '{DB_REPO_PATH}' was not found in your repository.")
        st.stop()
    
    st.write(f"✅ Source database '{DB_REPO_PATH}' found. Attempting to copy...")
    
    # Attempt to copy the file
    try:
        # Ensure the target directory exists before copying
        os.makedirs(os.path.dirname(DB_PERSISTENT_PATH), exist_ok=True)
        shutil.copy(DB_REPO_PATH, DB_PERSISTENT_PATH)
        st.write("✅ Database successfully copied to persistent storage.")
    except Exception as e:
        st.error(f"❌ Error: Failed to copy the database. The server reported an error: {e}")
        st.stop()

# Run the setup function
setup_database()
# =========================================

# 1️⃣ Connect to the persistent SQLite database
try:
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PERSISTENT_PATH}")
    st.write("✅ Successfully connected to the database.")
except Exception as e:
    st.error(f"❌ Error: Could not connect to the database at {DB_PERSISTENT_PATH}. Error: {e}")
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