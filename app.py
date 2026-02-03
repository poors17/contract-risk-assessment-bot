import streamlit as st
import spacy
import pdfplumber
import re
from spacy.lang.en import English

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Contract Risk Bot",
    page_icon="📄",
    layout="centered"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.title {
    text-align: center;
    color: #2E86C1;
}

.risk-high {
    background-color: #fdecea;
    border-left: 6px solid red;
    padding: 15px;
    border-radius: 10px;
    font-weight: bold;
}

.risk-low {
    background-color: #e9f7ef;
    border-left: 6px solid green;
    padding: 15px;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD NLP MODEL (SAFE) ----------------
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = English()
    nlp.add_pipe("sentencizer")

# ---------------- INITIALIZE VARIABLES ----------------
parties = []
dates = []
money = []

# ---------------- TITLE ----------------
st.markdown("""
<h1 class="title">📄 Contract Analysis & Risk Assessment Bot</h1>
<hr>
""", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📤 Upload Contract (PDF or TXT)", type=["pdf", "txt"]
)

text = ""

# ---------------- READ FILE ----------------
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        text = uploaded_file.read().decode("utf-8")

# ---------------- PROCESS TEXT ----------------
if text:

    # -------- CONTRACT TEXT --------
    st.markdown("""
    <div class="card">
        <h3>📌 Extracted Contract Text</h3>
    </div>
    """, unsafe_allow_html=True)

    st.text_area("Contract Text", text, height=220)

    # -------- NLP PROCESS --------
    doc = nlp(text)

    parties = list(set(ent.text for ent in doc.ents if ent.label_ == "ORG"))
    dates = list(set(ent.text for ent in doc.ents if ent.label_ == "DATE"))
    money = re.findall(r'₹\s?\d+(?:,\d+)*(?:\.\d+)?', text)

    # -------- FALLBACK EXTRACTION (IMPORTANT) --------
    if not parties:
        org_pattern = r'\b[A-Z][A-Za-z& ]+(?:Technologies|Solutions|Corporation|Ltd|Private Limited)\b'
        parties = list(set(re.findall(org_pattern, text)))

    if not dates:
        date_pattern = r'\b\d+\s+(?:months?|years?)\b'
        dates = list(set(re.findall(date_pattern, text)))

    # -------- DETAILS --------
    st.markdown("""
    <div class="card">
        <h3>🔍 Extracted Details</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**🏢 Parties:**")
    st.write(parties if parties else "Not detected")

    st.markdown("**📅 Dates:**")
    st.write(dates if dates else "Not detected")

    st.markdown("**💰 Amounts:**")
    st.write(money if money else "Not detected")

    # -------- RISK ANALYSIS --------
    risky_words = ["penalty", "terminate", "liability", "indemnity"]
    found_risks = [word for word in risky_words if word in text.lower()]

    if found_risks:
        st.markdown(f"""
        <div class="risk-high">
            ⚠️ Risk Level: HIGH <br>
            Reason: {", ".join(found_risks)}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="risk-low">
            ✅ Risk Level: LOW
        </div>
        """, unsafe_allow_html=True)

    # -------- SUMMARY --------
    st.markdown("""
    <div class="card">
        <h3>📝 Summary</h3>
        <p>
        This contract includes identified parties, time duration, and monetary values.
        Potential legal risks are highlighted based on sensitive clauses such as
        termination, penalties, and liabilities.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<hr>
<p style="text-align:center; color:gray;">
Built for GUVI × HCL Hackathon | Contract Analysis & Risk Assessment Bot
</p>
""", unsafe_allow_html=True)
