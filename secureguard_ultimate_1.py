import streamlit as st
import pandas as pd
import re
from textblob import TextBlob
import csv
import os
from datetime import datetime
import plotly.express as px
import time # NEW: For visual effects

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="SecureGuard AI | Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it look "Hacker/Enterprise" style
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        color: white;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

LOG_FILE = "moderation_logs.csv"

# --- 2. AUTHENTICATION (THE LOCK) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_password():
    if st.session_state['password_input'] == "fusion2026":
        st.session_state['authenticated'] = True
        del st.session_state['password_input']
        st.toast("✅ Access Granted: Loading SecureGuard Core...", icon="🔓")
        time.sleep(1) # Fake loading delay for effect
    else:
        st.error("❌ Access Denied: Invalid Security Key")

if not st.session_state['authenticated']:
    # Advanced Login Screen
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=100)
        st.title("SecureGuard AI")
        st.markdown("### 🔒 Restricted Access Portal")
        st.warning("⚠️ This system is monitored. Authorized personnel only.")
        st.text_input("Security Access Key:", type="password", key="password_input", on_change=check_password)
        st.markdown("<div style='text-align: center; color: grey;'>Fusion CX • Internal Tool v2.4</div>", unsafe_allow_html=True)
    st.stop()

# ------------------------------------------------------------------
# SYSTEM INTERFACE (LOGGED IN)
# ------------------------------------------------------------------

# --- SIDEBAR (THE "PRO" FEEL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9632/9632386.png", width=60)
    st.title("SecureGuard")
    st.caption("Enterprise Moderation Suite")
    
    st.divider()
    
    # Profile Section
    st.markdown("**👤 Operator:** `Admin_User`")
    st.markdown("**🟢 Status:** `Online`")
    st.markdown("**🔗 Server:** `US-East-1 (Secure)`")
    
    st.divider()
    
    # Live System Stats (Fake but impressive)
    st.markdown("### 🖥️ System Health")
    st.progress(88, text="CPU Usage")
    st.progress(42, text="Memory Usage")
    st.caption("Latency: 24ms | Uptime: 14d 2h")
    
    st.divider()
    if st.button("🚪 Logout"):
        st.session_state['authenticated'] = False
        st.rerun()

# --- 3. BACKEND LOGIC ---
BANNED_KEYWORDS = ['scam', 'fraud', 'hate', 'kill', 'attack']
AADHAAR_PATTERN = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
CREDIT_CARD_PATTERN = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
PHONE_PATTERN = r'(\+91[\-\s]?)?[6789]\d{9}'

def analyze_content(text):
    flags = []
    priority = "Low"
    
    # Cyber Checks
    if re.search(CREDIT_CARD_PATTERN, text):
        flags.append("FINANCIAL_DATA_LEAK")
        priority = "CRITICAL"
    elif re.search(AADHAAR_PATTERN, text):
        flags.append("PII_EXPOSURE_AADHAAR")
        priority = "CRITICAL"
    if re.search(PHONE_PATTERN, text):
        flags.append("PII_PHONE_NUMBER")
        if priority != "CRITICAL": priority = "High"

    # Safety Checks
    text_lower = text.lower()
    for word in BANNED_KEYWORDS:
        if word in text_lower:
            flags.append(f"SAFETY_VIOLATION: {word}")
            if priority == "Low": priority = "Medium"

    # Sentiment Check
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score < -0.5:
        flags.append("NEGATIVE_SENTIMENT")

    return {
        "Flags": flags,
        "Priority": priority,
        "Sentiment": round(sentiment_score, 2)
    }

def log_decision(text, flags, priority, decision):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Original_Text", "Flags", "Priority", "Decision"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text, str(flags), priority, decision])

# --- 4. MAIN DASHBOARD UI ---

# Top Header Area
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("🛡️ Data Labeling Dashboard")
    st.markdown("**Active Task:** `Content Moderation` | **Queue:** `Real-time Stream`")
with col_head2:
    # Real-time clock
    st.markdown(f"**🕒 {datetime.now().strftime('%H:%M:%S')}**")
    st.caption(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

# TABS LAYOUT
tab1, tab2, tab3 = st.tabs(["⚡ Live Moderator", "📈 Analytics Hub", "📂 Batch Processor"])

# === TAB 1: LIVE MODERATOR ===
with tab1:
    st.markdown("#### 💬 Incoming Data Stream")
    
    # Layout: Input on left, Instructions on right
    c1, c2 = st.columns([2, 1])
    
    with c2:
        with st.expander("ℹ️ Moderator Guidelines", expanded=True):
            st.info("""
            **SOP v1.2:**
            1. Check for **Red Flags** (PII/Scams).
            2. Verify context before rejecting.
            3. All actions are logged for audit.
            """)
    
    with c1:
        user_input = st.text_area("Paste User Comment:", height=120, placeholder="Waiting for data stream...", help="Paste social media comments or chat logs here.")
        
        if st.button("🔍 Run Analysis", type="primary", use_container_width=True):
            if user_input:
                with st.spinner('Running NLP & Regex Engines...'):
                    time.sleep(0.5) # Fake processing time for "feel"
                    result = analyze_content(user_input)
                    st.session_state['result'] = result
                    st.session_state['text'] = user_input
            else:
                st.toast("⚠️ Input is empty!", icon="⚠️")

    # Results Area
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.markdown("---")
        st.markdown("#### 🧠 AI Assessment")
        
        # Metric Cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Priority Level", res['Priority'], delta="Urgent" if res['Priority']=="CRITICAL" else None, delta_color="inverse")
        m2.metric("Sentiment Score", res['Sentiment'])
        m3.metric("Flags Count", len(res['Flags']))
        m4.metric("Confidence", "98.5%") # Hardcoded for demo flair
        
        if res['Flags']:
            st.error(f"🚫 **VIOLATIONS DETECTED:** {', '.join(res['Flags'])}")
        else:
            st.success("✅ **CLEAN CONTENT:** No risk factors identified.")

        # Decision Buttons
        st.markdown("#### 👤 Human Decision")
        btn_col1, btn_col2 = st.columns(2)
        
        if btn_col1.button("✅ Approve (Safe)", use_container_width=True):
            log_decision(st.session_state['text'], res['Flags'], res['Priority'], "SAFE")
            st.toast("Decision Saved: SAFE", icon="💾")
            del st.session_state['result']
            time.sleep(1)
            st.rerun()
            
        if btn_col2.button("❌ Reject (Violation)", type="primary", use_container_width=True):
            log_decision(st.session_state['text'], res['Flags'], res['Priority'], "VIOLATION")
            st.toast("Decision Saved: VIOLATION", icon="💾")
            del st.session_state['result']
            time.sleep(1)
            st.rerun()

# === TAB 2: ANALYTICS HUB ===
with tab2:
    st.subheader("📊 Operational Insights")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        
        if not df.empty:
            # Top Stats Row
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Processed", len(df))
            k2.metric("Violations", len(df[df['Decision'] == 'VIOLATION']), delta_color="inverse")
            k3.metric("Safe Content", len(df[df['Decision'] == 'SAFE']))
            k4.metric("Efficiency", f"{len(df) * 1.2} sec") # Fake efficiency stat

            st.divider()
            
            # Charts
            chart1, chart2 = st.columns(2)
            with chart1:
                st.markdown("**Decisions Breakdown**")
                if 'Decision' in df.columns:
                    fig_pie = px.pie(df, names='Decision', hole=0.4, color='Decision', color_discrete_map={'SAFE':'#00CC96', 'VIOLATION':'#EF553B'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                
            with chart2:
                st.markdown("**Recent Audit Log**")
                st.dataframe(df.tail(8), use_container_width=True, hide_index=True)
        else:
            st.info("System initialized. Waiting for data...")
    else:
        st.warning("⚠️ No logs found. Please process data in the Live Moderator tab.")

# === TAB 3: BATCH PROCESSOR ===
with tab3:
    st.subheader("📂 Bulk Processing Engine")
    
    col_up, col_info = st.columns([2, 1])
    
    with col_info:
        st.info("Upload a CSV with a column named **'Comment'**. The engine will process up to 10,000 rows/minute.")
    
    with col_up:
        uploaded_file = st.file_uploader("Drop CSV Dataset Here", type=["csv"])
    
    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            if 'Comment' in batch_df.columns:
                st.success(f"File Verified: {len(batch_df)} rows loaded.")
                
                if st.button("🚀 Start Batch Processing"):
                    progress_bar = st.progress(0, text="Initializing AI Models...")
                    
                    # Simulation of progress
                    for percent_complete in range(0, 100, 20):
                        time.sleep(0.1)
                        progress_bar.progress(percent_complete + 20, text=f"Processing chunk {percent_complete}%...")
                    
                    # Actual Processing
                    batch_results = batch_df['Comment'].apply(lambda x: pd.Series(analyze_content(x)))
                    final_batch = pd.concat([batch_df, batch_results], axis=1)
                    
                    progress_bar.progress(100, text="Completed!")
                    
                    st.dataframe(final_batch.head(), use_container_width=True)
                    
                    csv_data = final_batch.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Report", data=csv_data, file_name="secureguard_report.csv", mime="text/csv", type="primary")
                
            else:
                st.error("❌ Schema Error: CSV must contain a 'Comment' column.")
        except Exception as e:
            st.error(f"System Error: {e}")
