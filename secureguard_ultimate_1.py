import streamlit as st
import pandas as pd
import re
from textblob import TextBlob
import csv
import os
from datetime import datetime
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="SecureGuard AI Enterprise", page_icon="🛡️", layout="wide")
LOG_FILE = "moderation_logs.csv"

# --- 2. AUTHENTICATION (THE LOCK) ---
# This section prevents anyone without the password from seeing the app
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_password():
    if st.session_state['password_input'] == "fusion2026": # <--- PASSWORD IS HERE
        st.session_state['authenticated'] = True
        del st.session_state['password_input']
    else:
        st.error("❌ Incorrect Access Key")

if not st.session_state['authenticated']:
    st.markdown("## 🔒 SecureGuard AI - Restricted Access")
    st.markdown("This tool is access to very few person")
    st.text_input("Enter Access Key:", type="password", key="password_input", on_change=check_password)
    st.stop() # Stops the app here if not logged in

# ------------------------------------------------------------------
# EVERYTHING BELOW THIS LINE ONLY RUNS IF PASSWORD IS CORRECT
# ------------------------------------------------------------------

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

# --- 4. THE UI ARCHITECTURE ---

st.title("🛡️ SecureGuard AI: Enterprise Dashboard")
st.markdown("### Integrated AI Process & Analytics Suite")

# TABS LAYOUT
tab1, tab2, tab3 = st.tabs(["⚡ Live Moderator", "📈 Analytics Hub", "📂 Batch Processor"])

# === TAB 1: LIVE MODERATOR ===
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        user_input = st.text_area("Live Data Stream:", height=100, placeholder="Paste user comment here...")
        if st.button("🔍 Analyze Content", key="btn_analyze"):
            if user_input:
                result = analyze_content(user_input)
                st.session_state['result'] = result
                st.session_state['text'] = user_input
            else:
                st.warning("Enter text first.")

    # Results Area
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Priority", res['Priority'], delta_color="inverse" if res['Priority']=="CRITICAL" else "normal")
        m2.metric("Sentiment", res['Sentiment'])
        m3.metric("Flags Detected", len(res['Flags']))
        
        if res['Flags']:
            st.error(f"Violations: {', '.join(res['Flags'])}")
        else:
            st.success("Clean Content")

        c1, c2 = st.columns(2)
        if c1.button("✅ Approve", use_container_width=True):
            log_decision(st.session_state['text'], res['Flags'], res['Priority'], "SAFE")
            st.success("Logged: SAFE")
            del st.session_state['result']
            st.rerun()
        if c2.button("❌ Reject", use_container_width=True):
            log_decision(st.session_state['text'], res['Flags'], res['Priority'], "VIOLATION")
            st.error("Logged: VIOLATION")
            del st.session_state['result']
            st.rerun()

# === TAB 2: ANALYTICS HUB ===
with tab2:
    st.subheader("📊 Operational Insights")
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        
        if not df.empty:
            # Top Row Stats
            k1, k2, k3 = st.columns(3)
            k1.metric("Total Processed", len(df))
            k2.metric("Violations Found", len(df[df['Decision'] == 'VIOLATION']))
            k3.metric("Safe Content", len(df[df['Decision'] == 'SAFE']))
            
            st.divider()
            
            # Charts Row
            chart1, chart2 = st.columns(2)
            
            with chart1:
                st.caption("Distribution of Decisions")
                if 'Decision' in df.columns:
                    fig_pie = px.pie(df, names='Decision', title='Safe vs Violation Ratio', color='Decision', color_discrete_map={'SAFE':'green', 'VIOLATION':'red'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                
            with chart2:
                st.caption("Recent Activity Log")
                st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("Log file exists but is empty. Process data first.")
            
    else:
        st.info("No data available. Go to 'Live Moderator' or 'Batch Processor' to generate data!")

# === TAB 3: BATCH PROCESSOR ===
with tab3:
    st.subheader("📂 Bulk CSV Processor")
    st.markdown("Upload a CSV file containing a column named **'Comment'** to process thousands of rows instantly.")
    
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            if 'Comment' in batch_df.columns:
                st.info(f"Loaded {len(batch_df)} rows. Processing...")
                
                # Apply Analysis to ALL rows
                batch_results = batch_df['Comment'].apply(lambda x: pd.Series(analyze_content(x)))
                
                # Combine original data with results
                final_batch = pd.concat([batch_df, batch_results], axis=1)
                
                st.success("Processing Complete!")
                st.dataframe(final_batch.head())
                
                # Allow Download
                csv_data = final_batch.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Processed Report", data=csv_data, file_name="batch_report_processed.csv", mime="text/csv")
                
            else:
                st.error("CSV must contain a column named 'Comment'.")
        except Exception as e:
            st.error(f"Error processing file: {e}")
