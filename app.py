import streamlit as st
import pandas as pd
import re
import emoji
import io
import unicodedata
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="CleanStream AI | Social Media Comment Cleaner",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'cleaned_results' not in st.session_state:
    st.session_state.cleaned_results = []
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Modern Custom CSS with Gradients and Animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Content container with glassmorphism */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 3rem 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Hero Header */
    .hero-header {
        text-align: center;
        padding: 2rem 0 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradient 3s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #64748b;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Custom Cards */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .custom-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 20px 25px -5px rgba(102, 126, 234, 0.5);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.9;
    }
    
    /* Platform Badges - Enhanced */
    .platform-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .platform-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    .badge-instagram { 
        background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
        color: white;
    }
    .badge-youtube { 
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%);
        color: white;
    }
    .badge-tiktok { 
        background: linear-gradient(135deg, #000000 0%, #EE1D52 50%, #69C9D0 100%);
        color: white;
    }
    .badge-reddit { 
        background: linear-gradient(135deg, #FF4500 0%, #FF5722 100%);
        color: white;
    }
    .badge-facebook { 
        background: linear-gradient(135deg, #1877F2 0%, #0C63D4 100%);
        color: white;
    }
    .badge-twitter { 
        background: linear-gradient(135deg, #1DA1F2 0%, #0C85D0 100%);
        color: white;
    }
    .badge-linkedin { 
        background: linear-gradient(135deg, #0077B5 0%, #005885 100%);
        color: white;
    }
    .badge-other { 
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px dashed #cbd5e0;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Buttons - Enhanced */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar Styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .sidebar-content, [data-testid="stSidebar"] > div:first-child {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 0;
    }
    
    /* File Uploader Custom Style */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        border: 2px dashed #cbd5e0;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
    }
    
    /* Expander Custom Style */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Success/Error/Info Messages */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Feature Card */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1e293b;
    }
    
    .feature-description {
        font-size: 0.875rem;
        color: #64748b;
        line-height: 1.6;
    }
    
    /* Animated Background Pattern */
    .pattern-bg {
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
        animation: pattern-move 20s ease infinite;
    }
    
    @keyframes pattern-move {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 100% 100%; }
    }
    
    /* Language Badge */
    .language-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    /* Section Divider */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
        margin: 3rem 0;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    /* Results Card */
    .results-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .results-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    
    .results-card.instagram { border-left-color: #E1306C; }
    .results-card.youtube { border-left-color: #FF0000; }
    .results-card.tiktok { border-left-color: #000000; }
    .results-card.reddit { border-left-color: #FF4500; }
    .results-card.facebook { border-left-color: #1877F2; }
    .results-card.twitter { border-left-color: #1DA1F2; }
    .results-card.linkedin { border-left-color: #0077B5; }
    
    /* Pulse Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Download Button Custom */
    .download-button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.4);
    }
    
    .download-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.6);
    }
    </style>
""", unsafe_allow_html=True)

class CommentCleaner:
    """Multilingual social media comment cleaning engine"""
    
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
        """Detect primary script/writing system in text"""
        if pd.isna(text) or not text:
            return 'unknown'
        
        text = str(text)
        script_counts = {
            'cjk': 0,
            'thai': 0,
            'devanagari': 0,
            'arabic': 0,
            'cyrillic': 0,
            'latin': 0,
            'other': 0
        }
        
        for char in text:
            if '\u4e00' <= char <= '\u9fff' or '\u3040' <= char <= '\u30ff' or '\uac00' <= char <= '\ud7af':
                script_counts['cjk'] += 1
            elif '\u0e00' <= char <= '\u0e7f':
                script_counts['thai'] += 1
            elif '\u0900' <= char <= '\u097f':
                script_counts['devanagari'] += 1
            elif '\u0600' <= char <= '\u06ff':
                script_counts['arabic'] += 1
            elif '\u0400' <= char <= '\u04ff':
                script_counts['cyrillic'] += 1
            elif char.isalpha() and ord(char) < 128:
                script_counts['latin'] += 1
        
        return max(script_counts, key=script_counts.get)
    
    def has_meaningful_content(self, text):
        """Check if text contains meaningful linguistic content (multilingual)"""
        if pd.isna(text) or not text:
            return False
        
        text = str(text).strip()
        text_no_emoji = emoji.replace_emoji(text, replace='')
        text_clean = text_no_emoji.strip()
        
        if not text_clean:
            return False
        
        letter_count = sum(1 for char in text_clean if unicodedata.category(char).startswith('L'))
        
        if letter_count >= 2:
            return True
        
        if all(unicodedata.category(char) in ['Po', 'Ps', 'Pe', 'Pd', 'Pc', 'Sk', 'Sm', 'Zs'] 
               for char in text_clean if char.strip()):
            return False
        
        return letter_count > 0
    
    def get_adaptive_min_length(self, text):
        """Adjust minimum length based on detected script"""
        script = self.detect_script_type(text)
        
        if script == 'cjk':
            return max(3, self.min_char_length // 3)
        elif script == 'thai':
            return max(5, self.min_char_length // 2)
        elif script in ['devanagari', 'arabic']:
            return max(5, int(self.min_char_length * 0.6))
        else:
            return self.min_char_length
        
    def remove_emojis(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        return emoji.replace_emoji(text, replace='')
    
    def remove_urls(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        text = re.sub(url_pattern, '', text)
        text = re.sub(r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
        return text
    
    def remove_mentions(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        return re.sub(r'@[\w\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0e00-\u0e7f\u0900-\u097f]+', '', text)
    
    def remove_hashtags(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        return re.sub(r'#[\w\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0e00-\u0e7f\u0900-\u097f]+', '', text)
    
    def clean_whitespace(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_special_chars(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        text = re.sub(r'([!?.]){3,}', r'\1', text)
        return text
    
    def is_blank_or_empty(self, text):
        if pd.isna(text):
            return True
        if text == '':
            return True
        if str(text).strip() == '':
            return True
        return False
    
    def is_only_emojis(self, text):
        if pd.isna(text):
            return False
        no_emoji = emoji.replace_emoji(str(text), replace='')
        return no_emoji.strip() == ''
    
    def calculate_word_count(self, text):
        """Language-aware word counting"""
        if pd.isna(text) or not text:
            return 0
        
        text = str(text).strip()
        script = self.detect_script_type(text)
        
        if script == 'cjk':
            return sum(1 for char in text if '\u4e00' <= char <= '\u9fff' or 
                      '\u3040' <= char <= '\u30ff' or '\uac00' <= char <= '\ud7af')
        elif script == 'thai':
            thai_chars = sum(1 for char in text if '\u0e00' <= char <= '\u0e7f')
            return max(1, thai_chars // 4)
        else:
            words = text.split()
            return len([w for w in words if len(w) > 0])
    
    def is_valid_comment(self, text, min_length):
        """Multilingual validation logic"""
        if pd.isna(text) or text == '':
            self.removed_rows['blank_empty'] += 1
            return False
        
        cleaned = str(text).strip()
        
        if cleaned == '':
            self.removed_rows['blank_empty'] += 1
            return False
        
        if not self.has_meaningful_content(cleaned):
            self.removed_rows['only_special_chars'] += 1
            return False
        
        adaptive_min = self.get_adaptive_min_length(cleaned)
        
        if len(cleaned) < adaptive_min:
            self.removed_rows['too_short'] += 1
            return False
            
        return True
    
    def detect_comment_column(self, df):
        """Detect comment column in multiple languages"""
        columns_lower = [col.lower() for col in df.columns]
        
        comment_keywords = ['text', 'comment', 'content', 'message', 'caption',
                           '评论', '內容', 'コメント', 'ความคิดเห็น', 'टिप्पणी']
        
        for keyword in comment_keywords:
            if keyword in columns_lower:
                idx = columns_lower.index(keyword)
                return df.columns[idx]
        
        return None
    
    def clean_dataset(self, df, comment_column=None, 
                     remove_emoji=True, 
                     remove_url=True,
                     remove_mention=False,
                     remove_hashtag=False,
                     min_length=None):
        
        if comment_column is None:
            comment_column = self.detect_comment_column(df)
            if comment_column is None:
                return None, "Could not detect comment column. Available columns: " + ", ".join(df.columns)
        
        if comment_column not in df.columns:
            return None, f"Column '{comment_column}' not found in dataset"
        
        if min_length is None:
            min_length = self.min_char_length
        
        original_count = len(df)
        original_comment_col = comment_column
        
        self.removed_rows = {
            'blank_empty': 0,
            'too_short': 0,
            'only_special_chars': 0,
            'only_emojis': 0
        }
        
        df = df[~df[comment_column].apply(self.is_blank_or_empty)].copy()
        blanks_removed = original_count - len(df)
        
        if remove_emoji:
            emoji_only_mask = df[comment_column].apply(self.is_only_emojis)
            emoji_only_count = emoji_only_mask.sum()
            self.removed_rows['only_emojis'] = emoji_only_count
            df = df[~emoji_only_mask].copy()
        
        df['cleaned_comment'] = df[comment_column].copy()
        
        if remove_url:
            df['cleaned_comment'] = df['cleaned_comment'].apply(self.remove_urls)
        
        if remove_mention:
            df['cleaned_comment'] = df['cleaned_comment'].apply(self.remove_mentions)
        
        if remove_hashtag:
            df['cleaned_comment'] = df['cleaned_comment'].apply(self.remove_hashtags)
        
        df['cleaned_comment'] = df['cleaned_comment'].apply(self.remove_special_chars)
        df['cleaned_comment'] = df['cleaned_comment'].apply(self.clean_whitespace)
        
        df['char_count'] = df['cleaned_comment'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
        df['word_count'] = df['cleaned_comment'].apply(self.calculate_word_count)
        
        df['is_valid'] = df['cleaned_comment'].apply(lambda x: self.is_valid_comment(x, min_length))
        df_cleaned = df[df['is_valid']].copy()
        df_cleaned = df_cleaned.drop('is_valid', axis=1)
        
        final_count = len(df_cleaned)
        self.cleaning_stats = {
            'original_count': original_count,
            'after_blank_removal': original_count - blanks_removed,
            'final_count': final_count,
            'total_removed': original_count - final_count,
            'retention_rate': round((final_count / original_count) * 100, 2) if original_count > 0 else 0
        }
        
        self.preview_data = df_cleaned[['cleaned_comment']].copy()
        
        df_cleaned[original_comment_col] = df_cleaned['cleaned_comment']
        df_cleaned = df_cleaned.drop(['cleaned_comment', 'char_count', 'word_count'], axis=1)
        
        return df_cleaned, None

# Hero Header
st.markdown("""
    <div class="hero-header">
        <div class="hero-title">✨ CleanStream AI</div>
        <div class="hero-subtitle">Transform messy social data into actionable insights • Supports 50+ languages globally</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar configuration with modern styling
with st.sidebar:
    st.markdown("### ⚙️ Configuration Panel")
    st.markdown("---")
    
    min_length = st.slider(
        "📏 Minimum Character Length",
        min_value=5,
        max_value=50,
        value=10,
        help="Auto-adjusts for different writing systems"
    )
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 12px; color: white; margin: 1rem 0;'>
            <strong>🌍 Adaptive Thresholds:</strong><br>
            • CJK Languages: 3 chars<br>
            • Thai/Khmer: 5 chars<br>
            • Indic Scripts: 6 chars<br>
            • Latin Scripts: 10 chars
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Cleaning Options")
    remove_emoji = st.checkbox("🎭 Remove emoji-only comments", value=True)
    remove_url = st.checkbox("🔗 Remove URLs", value=True)
    remove_mention = st.checkbox("@ Remove mentions", value=False)
    remove_hashtag = st.checkbox("# Remove hashtags", value=False)
    
    st.markdown("---")
    st.markdown("### 📦 Export Settings")
    split_files = st.checkbox("📑 Auto-split large files (10k+ rows)", value=True)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🌏</div>
            <div style='font-size: 0.875rem; color: #64748b;'>
                <strong>50+ Languages</strong><br>
                Powered by Unicode Analysis
            </div>
        </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Upload Your Data")
    uploaded_files = st.file_uploader(
        "Drag and drop files here or click to browse",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        help="Support for CSV and Excel formats"
    )
    
    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} file(s) ready for processing")

with col2:
    st.markdown("### 💡 Quick Start")
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">1️⃣</div>
            <div class="feature-description">Upload your files</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">2️⃣</div>
            <div class="feature-description">Label platforms</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">3️⃣</div>
            <div class="feature-description">Clean & download</div>
        </div>
    """, unsafe_allow_html=True)

if uploaded_files:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Platform labeling section
    st.markdown("### 🏷️ Platform Classification")
    st.markdown("Assign each dataset to its source platform for organized processing:")
    
    file_platforms = {}
    
    # Create grid layout for platform selection
    num_cols = min(len(uploaded_files), 3)
    cols = st.columns(num_cols)
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % num_cols]:
            st.markdown(f"""
                <div class="custom-card">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; color: #1e293b;">
                        📄 {uploaded_file.name}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            platform = st.selectbox(
                "Select platform",
                ["Instagram", "YouTube", "TikTok", "Reddit", "Facebook", "Twitter", "LinkedIn", "Other"],
                key=f"platform_{idx}",
                index=0,
                label_visibility="collapsed"
            )
            file_platforms[uploaded_file.name] = platform
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Cleaning Process", type="primary", use_container_width=True):
            st.session_state.cleaned_results = []
            st.session_state.processing_complete = False
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    progress = (idx + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.markdown(f"**Processing:** {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")
                    
                    file_extension = uploaded_file.name.lower().split('.')[-1]
                    
                    if file_extension == 'csv':
                        try:
                            df = pd.read_csv(uploaded_file, encoding='utf-8')
                        except:
                            uploaded_file.seek(0)
                            try:
                                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                            except:
                                uploaded_file.seek(0)
                                df = pd.read_csv(uploaded_file, encoding='latin-1')
                    elif file_extension in ['xlsx', 'xls']:
                        df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else None)
                    else:
                        continue
                    
                    cleaner = CommentCleaner(min_char_length=min_length)
                    detected_col = cleaner.detect_comment_column(df)
                    
                    if not detected_col:
                        st.error(f"❌ {uploaded_file.name}: Could not detect comment column")
                        continue
                    
                    cleaned_df, error = cleaner.clean_dataset(
                        df,
                        comment_column=detected_col,
                        remove_emoji=remove_emoji,
                        remove_url=remove_url,
                        remove_mention=remove_mention,
                        remove_hashtag=remove_hashtag,
                        min_length=min_length
                    )
                    
                    if error:
                        st.error(f"❌ {uploaded_file.name}: {error}")
                        continue
                    
                    st.session_state.cleaned_results.append({
                        'filename': uploaded_file.name,
                        'platform': file_platforms[uploaded_file.name],
                        'cleaned_df': cleaned_df,
                        'stats': cleaner.cleaning_stats.copy(),
                        'removed': cleaner.removed_rows.copy(),
                        'preview': cleaner.preview_data.copy()
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            
            progress_bar.progress(1.0)
            status_text.markdown("✅ **All files processed successfully!**")
            st.session_state.processing_complete = True
            st.rerun()

# Display results
if st.session_state.processing_complete and st.session_state.cleaned_results:
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📊 Processing Results")
    
    # Overall summary metrics
    total_original = sum(r['stats']['original_count'] for r in st.session_state.cleaned_results)
    total_cleaned = sum(r['stats']['final_count'] for r in st.session_state.cleaned_results)
    total_removed = total_original - total_cleaned
    overall_retention = round((total_cleaned / total_original) * 100, 2) if total_original > 0 else 0
    
    # Create metric cards
    metric_cols = st.columns(4)
    
    metrics_data = [
        ("📥 Total Original", f"{total_original:,}", "#667eea"),
        ("✅ Total Cleaned", f"{total_cleaned:,}", "#10b981"),
        ("🗑️ Total Removed", f"{total_removed:,}", "#ef4444"),
        ("📈 Retention Rate", f"{overall_retention}%", "#f59e0b")
    ]
    
    for col, (label, value, color) in zip(metric_cols, metrics_data):
        with col:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Create visualization
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Processing summary chart
    chart_data = pd.DataFrame([
        {'File': r['filename'][:20] + '...' if len(r['filename']) > 20 else r['filename'],
         'Original': r['stats']['original_count'],
         'Cleaned': r['stats']['final_count'],
         'Removed': r['stats']['total_removed']}
        for r in st.session_state.cleaned_results
    ])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Original', x=chart_data['File'], y=chart_data['Original'],
                         marker_color='#667eea'))
    fig.add_trace(go.Bar(name='Cleaned', x=chart_data['File'], y=chart_data['Cleaned'],
                         marker_color='#10b981'))
    
    fig.update_layout(
        title="Processing Summary by File",
        barmode='group',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Individual file results
    for idx, result in enumerate(st.session_state.cleaned_results):
        platform_class = result['platform'].lower().replace(' ', '-')
        
        st.markdown(f"""
            <div class="results-card {platform_class}">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                    <div>
                        <span class='platform-badge badge-{platform_class}'>{result['platform']}</span>
                        <h3 style="display: inline; margin-left: 1rem; color: #1e293b;">{result['filename']}</h3>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Stats grid
        stat_cols = st.columns(4)
        stats_info = [
            ("📥 Original", result['stats']['original_count']),
            ("✨ Cleaned", result['stats']['final_count']),
            ("🗑️ Removed", result['stats']['total_removed']),
            ("📊 Retention", f"{result['stats']['retention_rate']}%")
        ]
        
        for col, (label, value) in zip(stat_cols, stats_info):
            with col:
                st.metric(label, value)
        
        # Detailed breakdown
        with st.expander(f"🔍 Detailed Analysis - {result['filename']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Removal Breakdown:**")
                removal_df = pd.DataFrame([
                    {"Category": "Blank/Empty", "Count": result['removed']['blank_empty']},
                    {"Category": "Emoji-only", "Count": result['removed']['only_emojis']},
                    {"Category": "Too Short", "Count": result['removed']['too_short']},
                    {"Category": "Special Chars", "Count": result['removed']['only_special_chars']}
                ])
                
                fig_pie = px.pie(removal_df, values='Count', names='Category',
                                color_discrete_sequence=px.colors.sequential.RdBu)
                fig_pie.update_layout(height=300)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("**Removal Details:**")
                for key, value in result['removed'].items():
                    st.markdown(f"• **{key.replace('_', ' ').title()}:** {value:,}")
        
        # Preview section
        with st.expander(f"👀 Sample Output - {result['filename']}"):
            st.dataframe(result['preview'].head(10), use_container_width=True, height=300)
        
        # Download section
        st.markdown(f"### 💾 Download Options")
        
        cleaned_df = result['cleaned_df']
        CHUNK_SIZE = 10000
        total_rows = len(cleaned_df)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = result['filename'].rsplit('.', 1)[0]
        platform_prefix = result['platform'].lower().replace(' ', '_')
        
        if total_rows > CHUNK_SIZE and split_files:
            num_files = (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE > 0 else 0)
            
            st.info(f"📦 Dataset will be split into {num_files} files ({CHUNK_SIZE:,} rows each)")
            
            download_cols = st.columns(min(num_files, 4))
            
            for i in range(num_files):
                with download_cols[i % 4]:
                    start_idx = i * CHUNK_SIZE
                    end_idx = min((i + 1) * CHUNK_SIZE, total_rows)
                    chunk_df = cleaned_df.iloc[start_idx:end_idx]
                    
                    st.markdown(f"**Part {i+1}**")
                    st.caption(f"{len(chunk_df):,} rows")
                    
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        chunk_df.to_excel(writer, index=False)
                    excel_data = output.getvalue()
                    
                    excel_filename = f"{platform_prefix}_{base_name}_part{i+1}_{timestamp}.xlsx"
                    
                    st.download_button(
                        label=f"📥 Excel Part {i+1}",
                        data=excel_data,
                        file_name=excel_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key=f"excel_{idx}_{i}"
                    )
        
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    cleaned_df.to_excel(writer, index=False)
                excel_data = output.getvalue()
                
                excel_filename = f"{platform_prefix}_{base_name}_{timestamp}.xlsx"
                
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"excel_single_{idx}"
                )
            
            with col2:
                csv_data = ('\ufeff' + cleaned_df.to_csv(index=False)).encode('utf-8')
                csv_filename = f"{platform_prefix}_{base_name}_{timestamp}.csv"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv",
                    use_container_width=True,
                    key=f"csv_single_{idx}"
                )
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Reset button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Process New Files", use_container_width=True):
            st.session_state.cleaned_results = []
            st.session_state.processing_complete = False
            st.rerun()

else:
    # Empty state with features
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("## 🌟 Key Features")
    
    feature_cols = st.columns(3)
    
    features = [
        ("🌍", "Multilingual Support", "Process comments in 50+ languages with Unicode-aware cleaning"),
        ("⚡", "Batch Processing", "Upload and process multiple files simultaneously"),
        ("🎯", "Smart Detection", "Auto-detects writing systems and applies adaptive thresholds"),
        ("📊", "Visual Analytics", "Interactive charts showing processing results"),
        ("🔒", "Privacy First", "All processing happens locally - no data stored"),
        ("📦", "Flexible Export", "Download as Excel or CSV with auto-splitting for large datasets")
    ]
    
    for col, (icon, title, desc) in zip(feature_cols * 2, features):
        with col:
            st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-description">{desc}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Language support showcase
    st.markdown("## 🌏 Global Language Support")
    
    lang_cols = st.columns(4)
    
    languages = [
        ("East Asia", ["🇨🇳 Chinese", "🇯🇵 Japanese", "🇰🇷 Korean"]),
        ("Southeast Asia", ["🇹🇭 Thai", "🇻🇳 Vietnamese", "🇮🇩 Indonesian"]),
        ("South Asia", ["🇮🇳 Hindi", "🇮🇳 Tamil", "🇮🇳 Telugu"]),
        ("Europe & Middle East", ["🇪🇸 Spanish", "🇷🇺 Russian", "🇸🇦 Arabic"])
    ]
    
    for col, (region, langs) in zip(lang_cols, languages):
        with col:
            st.markdown(f"**{region}**")
            for lang in langs:
                st.markdown(f"• {lang}")

# Footer
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 2rem; color: #64748b;'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>✨ CleanStream AI</div>
        <div style='font-size: 0.875rem;'>
            Powered by Unicode Intelligence • Built for Global Teams • Data Processed Locally
        </div>
        <div style='margin-top: 1rem; font-size: 0.75rem; opacity: 0.7;'>
            v2.0 | Supporting 50+ Languages Worldwide
        </div>
    </div>
""", unsafe_allow_html=True)
