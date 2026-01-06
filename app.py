import streamlit as st
import pandas as pd
import re
import emoji
import io
import unicodedata
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="CleanStream AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "cleaned_results" not in st.session_state:
    st.session_state.cleaned_results = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# ---------------------------------------------------------
# PREMIUM UI CSS
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: linear-gradient(180deg,#f8fafc,#eef2ff);
}

.glass-card {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 1.75rem;
    border: 1px solid rgba(148,163,184,0.25);
    box-shadow: 0 12px 32px rgba(15,23,42,0.08);
    margin-bottom: 1.5rem;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg,#667eea,#764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align:center;
}

.hero-subtitle {
    text-align:center;
    color:#64748b;
    margin-bottom:2rem;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    padding: 0.75rem 1.5rem;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#667eea,#764ba2);
    color: white;
    border-radius: 10px;
}

[data-testid="stMetric"] {
    background: white;
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

.stButton>button {
    background: linear-gradient(135deg,#667eea,#764ba2);
    color:white;
    border-radius:10px;
    font-weight:600;
    padding:0.7rem 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------
st.markdown("""
<div class="hero-title">✨ CleanStream AI</div>
<div class="hero-subtitle">
Transform messy social data into actionable insights • 50+ languages supported
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# COMMENT CLEANER ENGINE (UNCHANGED CORE LOGIC)
# ---------------------------------------------------------
class CommentCleaner:
    def __init__(self, min_char_length=10):
        self.min_char_length = min_char_length
        self.cleaning_stats = {}
        self.removed_rows = {
            'blank_empty': 0,
            'too_short': 0,
            'only_special_chars': 0,
            'only_emojis': 0
        }

    def detect_script_type(self, text):
        if not text or pd.isna(text):
            return "latin"
        for ch in str(text):
            if '\u4e00' <= ch <= '\u9fff':
                return "cjk"
            if '\u0e00' <= ch <= '\u0e7f':
                return "thai"
            if '\u0900' <= ch <= '\u097f':
                return "indic"
        return "latin"

    def adaptive_min(self, text):
        script = self.detect_script_type(text)
        if script == "cjk":
            return 3
        if script == "thai":
            return 5
        if script == "indic":
            return 6
        return self.min_char_length

    def clean(self, df, col, remove_emoji, remove_url):
        original = len(df)
        df = df.dropna(subset=[col])
        df[col] = df[col].astype(str)

        if remove_emoji:
            df[col] = df[col].apply(lambda x: emoji.replace_emoji(x, ""))

        if remove_url:
            df[col] = df[col].str.replace(r"http\S+|www\S+", "", regex=True)

        df[col] = df[col].str.strip()
        df["valid"] = df[col].apply(lambda x: len(x) >= self.adaptive_min(x))

        cleaned = df[df["valid"]].drop(columns=["valid"])

        self.cleaning_stats = {
            "original": original,
            "cleaned": len(cleaned),
            "removed": original - len(cleaned),
            "retention": round(len(cleaned)/original*100,2) if original else 0
        }

        return cleaned

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📤 Upload & Configure",
    "📊 Results Overview",
    "📁 File Details"
])

# ---------------------------------------------------------
# TAB 1 — UPLOAD & CONFIG
# ---------------------------------------------------------
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])

    with col1:
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=["csv","xlsx","xls"],
            accept_multiple_files=True
        )

    with col2:
        min_len = st.slider("Minimum characters",5,50,10)
        remove_emoji = st.checkbox("Remove emoji-only comments",True)
        remove_url = st.checkbox("Remove URLs",True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Run Cleaning", use_container_width=True):
        st.session_state.cleaned_results = []
        st.session_state.processing_complete = False

        for f in uploaded_files:
            df = pd.read_csv(f) if f.name.endswith("csv") else pd.read_excel(f)
            col = df.columns[0]

            cleaner = CommentCleaner(min_len)
            cleaned = cleaner.clean(df, col, remove_emoji, remove_url)

            st.session_state.cleaned_results.append({
                "name": f.name,
                "df": cleaned,
                "stats": cleaner.cleaning_stats
            })

        st.session_state.processing_complete = True
        st.success("✅ Processing complete!")

# ---------------------------------------------------------
# TAB 2 — OVERVIEW
# ---------------------------------------------------------
with tab2:
    if not st.session_state.processing_complete:
        st.info("Upload and process files to see results.")
    else:
        total_o = sum(r["stats"]["original"] for r in st.session_state.cleaned_results)
        total_c = sum(r["stats"]["cleaned"] for r in st.session_state.cleaned_results)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total Rows", total_o)
        c2.metric("Cleaned", total_c)
        c3.metric("Removed", total_o-total_c)
        c4.metric("Retention %", round(total_c/total_o*100,2))

# ---------------------------------------------------------
# TAB 3 — FILE DETAILS
# ---------------------------------------------------------
with tab3:
    for r in st.session_state.cleaned_results:
        with st.expander(f"📄 {r['name']}"):
            st.metric("Retention", f"{r['stats']['retention']}%")
            st.dataframe(r["df"].head(10), height=260)

            output = io.BytesIO()
            r["df"].to_excel(output,index=False)
            st.download_button(
                "📥 Download Excel",
                output.getvalue(),
                file_name=f"cleaned_{r['name']}"
            )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center;color:#64748b;padding:2rem">
CleanStream AI • Unicode-aware • Privacy-first • Built for global insights teams
</div>
""", unsafe_allow_html=True)
