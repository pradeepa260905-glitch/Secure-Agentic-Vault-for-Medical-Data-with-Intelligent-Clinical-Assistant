import streamlit as st
from cryptography.fernet import Fernet
import ollama
import base64
import io
from PyPDF2 import PdfReader 

# --- LAYER 1: INITIALIZATION ---
if 'vault' not in st.session_state:
    st.session_state.vault = {}  
if 'key' not in st.session_state:
    st.session_state.key = Fernet.generate_key() 
if 'is_verified' not in st.session_state:
    st.session_state.is_verified = False

# KEY FIX: Store the 'Unlocked' status so it stays open
if 'report_unlocked' not in st.session_state:
    st.session_state.report_unlocked = False
if 'current_report_name' not in st.session_state:
    st.session_state.current_report_name = ""

cipher = Fernet(st.session_state.key)

# --- LAYER 2: SIDEBAR LOGIN ---
st.sidebar.title("🔐 Portal Login")
role = st.sidebar.selectbox("Login As:", ["Patient", "Doctor"])
if role == "Doctor":
    doc_id = st.sidebar.text_input("License ID", value="DOC123")
    pin = st.sidebar.text_input("Security PIN", type="password", value="1234")
    if st.sidebar.button("Verify Identity"):
        if doc_id == "DOC123" and pin == "1234":
            st.session_state.is_verified = True
            st.sidebar.success("Identity Verified!")

# --- LAYER 3: MAIN UI ---
st.title("🛡️ Agentic Medical Vault")

# Upload Logic
uploaded_file = st.file_uploader("Upload Data", type=['pdf', 'png', 'jpg', 'mp4'])
if uploaded_file:
    if st.button(f"Encrypt '{uploaded_file.name}'"):
        st.session_state.vault[uploaded_file.name] = cipher.encrypt(uploaded_file.read())
        st.success("Encrypted!")

st.divider()
search_query = st.text_input("Search report name:")

# CLICKING THIS BUTTON "LOCKS" THE REPORT OPEN
if st.button("Submit Request"):
    if search_query in st.session_state.vault:
        if role == "Doctor" and st.session_state.is_verified:
            st.session_state.report_unlocked = True
            st.session_state.current_report_name = search_query
        else:
            st.error("Verified Doctor access only.")

# --- THE STABLE REPORT VIEW ---
if st.session_state.report_unlocked:
    target = st.session_state.current_report_name
    decrypted_bytes = cipher.decrypt(st.session_state.vault[target])
    file_ext = target.split('.')[-1].lower()
    
    st.subheader(f"📄 viewing: {target}")
    
    # Video Support
    if file_ext in ['mp4', 'mov']:
        st.video(decrypted_bytes)
    
    # PDF Support & Text Extraction
    report_text = ""
    if file_ext == 'pdf':
        reader = PdfReader(io.BytesIO(decrypted_bytes))
        for page in reader.pages:
            report_text += page.extract_text()
        base64_pdf = base64.b64encode(decrypted_bytes).decode('utf-8')
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400"></iframe>', unsafe_allow_html=True)

    # --- QUESTION TAP (Now stays open!) ---
    st.divider()
    st.subheader("📊 Intelligent Assistant")
    user_q = st.text_input("Ask a question about this report:")
    if st.button("Get Answer"):
        with st.spinner("Analyzing..."):
            res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': f"Report: {report_text}\n\nQuestion: {user_q}"}])
            st.info(res['message']['content'])

    if st.button("Close & Lock Report"):
        st.session_state.report_unlocked = False
        st.rerun()