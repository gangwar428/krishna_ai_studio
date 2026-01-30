import streamlit as st
import os, pandas as pd
from google import genai
from rembg import new_session
from ai_engine import analyze_with_gemini
from processor import master_process

# CLOUD PATHS (No C:\Users here)
CONFIG = {
    'WATCH_FOLDER': "Photos",
    'OUT_FINAL': "Final_Images",
    'BACKUP_DIR': "Originals_Backup",
    'LOG_FILE': "Product_Catalog.csv"
}

# Cloud par folders auto-create karne ke liye
for path in [CONFIG['WATCH_FOLDER'], CONFIG['OUT_FINAL'], CONFIG['BACKUP_DIR']]:
    if not os.path.exists(path):
        os.makedirs(path)

st.set_page_config("🛡️ KRISHNA v26 PRO", layout="wide")

# API Secrets (Cloud settings mein daalna padega)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
session = new_session("isnet-general-use")

# --- UI HEADER ---
head_col1, head_col2 = st.columns([5, 1])
with head_col1:
    st.title("🚀 KRISHNA Wide-Studio AI (v26)")
with head_col2:
    if st.button("🔄 REFRESH APP", width='stretch'):
        st.rerun()

# --- SIDEBAR UPLOADER ---
with st.sidebar:
    st.header("📤 Quick Upload")
    uploaded_files = st.file_uploader("Upload to Cloud Queue", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_path = os.path.join(CONFIG['WATCH_FOLDER'], uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("Uploaded!")
        st.rerun()

# --- CATALOG ---
if os.path.exists(CONFIG['LOG_FILE']):
    df = pd.read_csv(CONFIG['LOG_FILE'])
    st.dataframe(df.iloc[::-1], width='stretch', hide_index=True)

st.divider()
col_gal, col_sync = st.columns([2, 1])

# --- GALLERY ---
with col_gal:
    st.subheader("🖼️ Final Gallery")
    if os.path.exists(CONFIG['OUT_FINAL']):
        files = [f for f in os.listdir(CONFIG['OUT_FINAL']) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if files:
            files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(CONFIG['OUT_FINAL'], x)), reverse=True)[:8]
            cols = st.columns(2)
            for i, f in enumerate(files):
                with cols[i % 2]:
                    st.image(os.path.join(CONFIG['OUT_FINAL'], f), width='stretch')
                    r_bg = st.color_picker(f"New BG", "#FFFFFF", key=f"gal_cp_{f}")
                    if st.button(f"Update SKU {f.split('_')[0]}", key=f"gal_btn_{f}"):
                        sku_pre = f.split('_')[0]
                        for b_file in os.listdir(CONFIG['BACKUP_DIR']):
                            if b_file.startswith(sku_pre):
                                master_process(b_file, client, session, analyze_with_gemini, CONFIG, r_bg, CONFIG['BACKUP_DIR'], is_redo=True)
                                st.rerun()

# --- QUEUE ---
with col_sync:
    st.subheader("📦 Incoming Photos")
    incoming = [f for f in os.listdir(CONFIG['WATCH_FOLDER']) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    if incoming:
        for idx, f in enumerate(incoming):
            with st.container(border=True):
                st.image(os.path.join(CONFIG['WATCH_FOLDER'], f), width='stretch')
                i_bg = st.color_picker(f"Pick BG Color", "#F0F0F0", key=f"q_cp_{idx}_{f}")
                if st.button(f"✅ PROCESS", key=f"q_btn_{idx}_{f}"):
                    master_process(f, client, session, analyze_with_gemini, CONFIG, i_bg)
                    st.rerun()
    else:
        st.info("Queue empty.")
