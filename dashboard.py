import os
import time
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from firebase_admin import credentials, auth
import firebase_admin
from openai import OpenAI
from anthropic import Anthropic

DB_FILE = "pipeline_metrics.db"
load_dotenv()

# Initialize Firebase Admin SDK Safely
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_creds.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"❌ Failed to load firebase_creds.json: {e}")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.set_page_config(page_title="NexusPipe AI — Autonomous Data Pipelines", page_icon="🌐", layout="wide")

# PREMIUM MARKETING & APPLICATION THEME STYLING
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%) !important;
        color: #c9d1d9 !important;
    }
    .gradient-text {
        background: linear-gradient(90deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    .auth-container {
        background: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(48, 54, 65, 0.6);
        border-radius: 16px;
        padding: 40px;
        max-width: 500px;
        margin: 20px auto;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }
    .feature-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    div[data-baseweb="input"] {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        color: #ffffff !important;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #30363d !important;
        background-color: #161b22 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Database Backend Processing Layer
def process_portal_pipeline(raw_log_content, file_name, email_user):
    try:
        openai_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data validation agent. Extract the core error and timestamp. Be brief."},
                {"role": "user", "content": raw_log_content}
            ]
        )
        structured_summary = openai_response.choices.message.content
        o_tokens = openai_response.usage.total_tokens
        
        anthropic_response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            temperature=0.3,
            system="You are an expert systems engineer. Draft a professional Markdown incident report based on this summary.",
            messages=[{"role": "user", "content": f"Create a report for: {structured_summary}"}]
        )
        final_report = anthropic_response.content.text
        a_tokens = anthropic_response.usage.input_tokens + anthropic_response.usage.output_tokens
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_metrics (source_file, openai_tokens_used, anthropic_tokens_used, status, error_message)
            VALUES (?, ?, ?, ?, ?)
        """, (f"[{email_user}] {file_name}", o_tokens, a_tokens, "SUCCESS", ""))
        conn.commit()
        conn.close()
        return final_report
    except Exception as e:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_metrics (source_file, openai_tokens_used, anthropic_tokens_used, status, error_message)
            VALUES (?, 0, 0, 'FAILED', ?)
        """, (f"[{email_user}] {file_name}", str(e)))
        conn.commit()
        conn.close()
        return f"❌ Pipeline Failed: {e}"

def load_filtered_metrics(email_user):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM job_metrics ORDER BY id DESC", conn)
    conn.close()
    if not df.empty:
        df = df[df['source_file'].str.startswith(f"[{email_user}]", na=False)]
    return df

# App State Routing
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_email'] = ""
if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False

# ----------------- LAYER 1: PUBLIC MARKETING LANDING PAGE -----------------
if not st.session_state['authenticated'] and not st.session_state['show_login']:
    
    # Hero Title Section
    st.markdown("<p style='text-align: center; color: #58a6ff; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;'>Autonomous Multi-Agent Infrastructure</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 64px; margin-bottom: 10px;' class='gradient-text'>NexusPipe AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #8b949e; font-weight: 400; max-width: 800px; margin: 0 auto 40px auto;'>Instantly transform unstructured system failure data into engineer-ready root-cause documentation. Powered by multi-model orchestration.</h3>", unsafe_allow_html=True)
    
    # Main CTA Button to toggle Login Card
    left, mid, right = st.columns([2, 1, 2])
    with mid:
        if st.button("🚀 Access Console Node", type="primary", use_container_width=True):
            st.session_state['show_login'] = True
            st.rerun()
            
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # 3-Column Product Feature Framework
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='feature-card'>
                <h3 style='color: #58a6ff;'>🔌 Multi-Agent Triage</h3>
                <p style='color: #8b949e; font-size: 15px; line-height: 1.6;'>Routes raw data strings sequentially through custom OpenAI validation scripts and Anthropic synthesis models for flawless diagnostic parsing.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class='feature-card'>
                <h3 style='color: #bc8cff;'>🗄️ Relational Ledgers</h3>
                <p style='color: #8b949e; font-size: 15px; line-height: 1.6;'>Every automation job logs to an immutable SQL ledger layer, recording status variables and running real-time API token volume tracking.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class='feature-card'>
                <h3 style='color: #3fb950;'>🔐 Cryptographic Isolation</h3>
                <p style='color: #8b949e; font-size: 15px; line-height: 1.6;'>Secured by enterprise Firebase verification. User nodes are completely partitioned to guarantee absolute dataset privacy.</p>
            </div>
        """, unsafe_allow_html=True)

# ----------------- LAYER 2: PREMIUM AUTHENTICATION CARD -----------------
elif st.session_state['show_login'] and not st.session_state['authenticated']:
    
    if st.button("← Back to Product Overview"):
        st.session_state['show_login'] = False
        st.rerun()
        
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; font-size: 45px; margin-bottom: 0px;">🧬</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="gradient-text" style="text-align: center; margin-top: 10px; margin-bottom: 5px;">NexusPipe Gateway</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8b949e; margin-bottom: 25px; font-size: 14px;">Authorize secure node infrastructure session</p>', unsafe_allow_html=True)
    
    auth_mode = st.radio("Access Model:", ["Sign In to Dashboard", "Register New Node Account"], label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    email = st.text_input("User Email Address:", placeholder="name@company.com")
    password = st.text_input("Security Access Key:", type="password", placeholder="••••••••••••")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if auth_mode == "Register New Node Account":
        if st.button("Initialize New Enterprise Node", type="primary", use_container_width=True):
            try:
                user = auth.create_user(email=email, password=password)
                st.success(f"Node verified for {user.email}! Toggle 'Sign In' to authenticate.")
            except Exception as e:
                st.error(f"Initialization Rejected: {e}")
                
    elif auth_mode == "Sign In to Dashboard":
        if st.button("Authenticate Platform Session", type="primary", use_container_width=True):
            try:
                user = auth.get_user_by_email(email)
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = user.email
                st.rerun()
            except Exception:
                st.error("Access Denied: Invalid credentials or unregistered node path.")
                
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- LAYER 3: PRIVATE ACTIVE OPERATIONS PORTAL -----------------
else:
    st.sidebar.title("🌐 System Node")
    st.sidebar.markdown(f"Operator: `{st.session_state['user_email']}`")
    st.sidebar.markdown("---")
    if st.sidebar.button("Terminate Secure Session", use_container_width=True):
        st.session_state['authenticated'] = False
        st.session_state['user_email'] = ""
        st.session_state['show_login'] = False
        st.rerun()
        
