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
    page_title="CleanStream AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'cleaned_results' not in st.session_state:
    st.session_state.cleaned_results = []
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'file_platforms' not in st.session_state:
    st.session_state.file_platforms = {}

# FIXED CSS - Proper Sidebar Display
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* HIDE SIDEBAR COLLAPSE BUTTON */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* FORCE SIDEBAR TO STAY OPEN AND DISPLAY PROPERLY */
    section[data-testid="stSidebar"] {
        position: relative !important;
        min-width: 21rem !important;
        max-width: 21rem !important;
        transform: none !important;
        transition: none !important;
    }
    
    section[data-testid="stSidebar"] > div {
        transform: none !important;
        transition: none !important;
        width: 100% !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
    }
    
    /* Clean base */
    .stApp {
        background: #fafbfc;
    }
    
    .main .block-container {
        max-width: 1200px;
        padding: 2rem 1rem;
    }
    
    /* Compact header */
    .app-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 0.9rem;
        color: #718096;
    }
    
    /* Metrics */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: white;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.75rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Platform badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    
    .badge-instagram { background: #E1306C; }
    .badge-youtube { background: #FF0000; }
    .badge-tiktok { background: #000000; }
    .badge-reddit { background: #FF4500; }
    .badge-facebook { background: #1877F2; }
    .badge-twitter { background: #1DA1F2; }
    .badge-linkedin { background: #0077B5; }
    .badge-other { background: #6c757d; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #2d3748;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
    }
    
    .sidebar-info {
        background: #f7fafc;
        border-left: 3px solid #667eea;
        padding: 0.75rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #4a5568;
        margin: 1rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #5568d3;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 1rem 1.5rem 0 1.5rem;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 0;
        font-weight: 500;
        color: #718096;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom-color: #667eea;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #cbd5e0;
        border-radius: 8px;
        padding: 1.5rem;
        background: #f7fafc;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: white;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #f7fafc;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.9rem;
        color: #2d3748;
    }
    
    .streamlit-expanderHeader:hover {
        background: #edf2f7;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Messages */
    .stSuccess, .stError, .stInfo, .stWarning {
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Result item */
    .result-item {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .result-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .result-filename {
        font-weight: 600;
        color: #2d3748;
        font-size: 0.95rem;
    }
    
    /* Hide default streamlit metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
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
        if pd.isna(text) or not text:
            return 'unknown'
        
        text = str(text)
        script_counts = {
            'cjk': 0, 'thai': 0, 'devanagari': 0,
            'arabic': 0, 'cyrillic': 0, 'latin': 0, 'other': 0
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
        return emoji.replace_emoji(str(text), replace='')
    
    def remove_urls(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
        return text
    
    def remove_mentions(self, text):
        if pd.isna(text):
            return text
        return re.sub(r'@[\w\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0e00-\u0e7f\u0900-\u097f]+', '', str(text))
    
    def remove_hashtags(self, text):
        if pd.isna(text):
            return text
        return re.sub(r'#[\w\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af\u0e00-\u0e7f\u0900-\u097f]+', '', str(text))
    
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
        return re.sub(r'([!?.]){3,}', r'\1', text)
    
    def is_blank_or_empty(self, text):
        return pd.isna(text) or text == '' or str(text).strip() == ''
    
    def is_only_emojis(self, text):
        if pd.isna(text):
            return False
        no_emoji = emoji.replace_emoji(str(text), replace='')
        return no_emoji.strip() == ''
    
    def calculate_word_count(self, text):
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
        columns_lower = [col.lower() for col in df.columns]
        
        comment_keywords = ['text', 'comment', 'content', 'message', 'caption',
                           '评论', '內容', 'コメント', 'ความคิดเห็น', 'टिप्पणी']
        
        for keyword in comment_keywords:
            if keyword in columns_lower:
                idx = columns_lower.index(keyword)
                return df.columns[idx]
        
        return None
    
    def clean_dataset(self, df, comment_column=None, remove_emoji=True, remove_url=True,
                     remove_mention=False, remove_hashtag=False, min_length=None):
        
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
            'blank_empty': 0, 'too_short': 0,
            'only_special_chars': 0, 'only_emojis': 0
        }
        
        df = df[~df[comment_column].apply(self.is_blank_or_empty)].copy()
        
        if remove_emoji:
            emoji_only_mask = df[comment_column].apply(self.is_only_emojis)
            self.removed_rows['only_emojis'] = emoji_only_mask.sum()
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
            'final_count': final_count,
            'total_removed': original_count - final_count,
            'retention_rate': round((final_count / original_count) * 100, 2) if original_count > 0 else 0
        }
        
        self.preview_data = df_cleaned[['cleaned_comment']].copy()
        
        df_cleaned[original_comment_col] = df_cleaned['cleaned_comment']
        df_cleaned = df_cleaned.drop(['cleaned_comment', 'char_count', 'word_count'], axis=1)
        
        return df_cleaned, None

# Header
st.markdown("""
    <div class="app-header">
        <div class="app-title">✨ CleanStream AI</div>
        <div class="app-subtitle">Multilingual social media comment cleaner • 50+ languages supported</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    min_length = st.slider(
        "Minimum Character Length",
        min_value=5,
        max_value=50,
        value=10,
        help="Auto-adjusts for different scripts"
    )
    
    st.markdown("""
        <div class='sidebar-info'>
            <strong>🌍 Adaptive:</strong> CJK=3 chars, Thai=5 chars, Indic=6 chars, Latin=10 chars
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Cleaning Rules")
    remove_emoji = st.checkbox("Remove emoji-only", value=True)
    remove_url = st.checkbox("Remove URLs", value=True)
    remove_mention = st.checkbox("Remove @mentions", value=False)
    remove_hashtag = st.checkbox("Remove #hashtags", value=False)
    
    st.markdown("---")
    st.markdown("### 📦 Export")
    split_files = st.checkbox("Split large files (10k+ rows)", value=True)

# Main tabs
tab1, tab2 = st.tabs(["📤 Upload & Process", "📊 Results"])

with tab1:
    st.markdown("### Upload Files")
    uploaded_files = st.file_uploader(
        "Choose CSV or Excel files",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        help="Drag and drop or click to browse"
    )
    
    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} file(s) uploaded")
        
        st.markdown("### Label Platforms")
        
        cols = st.columns(min(len(uploaded_files), 3))
        
        for idx, uploaded_file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.caption(f"**{uploaded_file.name}**")
                platform = st.selectbox(
                    "Platform",
                    ["Instagram", "YouTube", "TikTok", "Reddit", "Facebook", "Twitter", "LinkedIn", "Other"],
                    key=f"platform_{idx}",
                    label_visibility="collapsed"
                )
                st.session_state.file_platforms[uploaded_file.name] = platform
        
        st.markdown("---")
        
        if st.button("🚀 Start Processing", type="primary", use_container_width=True):
            st.session_state.cleaned_results = []
            st.session_state.processing_complete = False
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                try:
                    progress = (idx + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    status_text.info(f"Processing: {uploaded_file.name} ({idx+1}/{len(uploaded_files)})")
                    
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
                        df, comment_column=detected_col,
                        remove_emoji=remove_emoji, remove_url=remove_url,
                        remove_mention=remove_mention, remove_hashtag=remove_hashtag,
                        min_length=min_length
                    )
                    
                    if error:
                        st.error(f"❌ {uploaded_file.name}: {error}")
                        continue
                    
                    st.session_state.cleaned_results.append({
                        'filename': uploaded_file.name,
                        'platform': st.session_state.file_platforms[uploaded_file.name],
                        'cleaned_df': cleaned_df,
                        'stats': cleaner.cleaning_stats.copy(),
                        'removed': cleaner.removed_rows.copy(),
                        'preview': cleaner.preview_data.copy()
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error: {uploaded_file.name} - {str(e)}")
            
            progress_bar.progress(1.0)
            status_text.success("✅ Processing complete! Switch to Results tab →")
            st.session_state.processing_complete = True
    
    else:
        st.info("👆 Upload files to get started")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🌍 Multilingual**")
            st.caption("50+ languages supported with adaptive thresholds")
        with col2:
            st.markdown("**⚡ Batch Processing**")
            st.caption("Process multiple files simultaneously")
        with col3:
            st.markdown("**🔒 Privacy First**")
            st.caption("All processing happens locally")

with tab2:
    if st.session_state.processing_complete and st.session_state.cleaned_results:
        
        total_original = sum(r['stats']['original_count'] for r in st.session_state.cleaned_results)
        total_cleaned = sum(r['stats']['final_count'] for r in st.session_state.cleaned_results)
        total_removed = total_original - total_cleaned
        overall_retention = round((total_cleaned / total_original) * 100, 2) if total_original > 0 else 0
        
        st.markdown("### Summary")
        
        st.markdown(f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-value">{total_original:,}</div>
                    <div class="metric-label">Original</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{total_cleaned:,}</div>
                    <div class="metric-label">Cleaned</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{total_removed:,}</div>
                    <div class="metric-label">Removed</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">{overall_retention}%</div>
                    <div class="metric-label">Retention</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### Processed Files")
        
        for idx, result in enumerate(st.session_state.cleaned_results):
            platform_class = result['platform'].lower().replace(' ', '-')
            
            with st.container():
                st.markdown(f"""
                    <div class="result-item">
                        <div class="result-header">
                            <span class='badge badge-{platform_class}'>{result['platform']}</span>
                            <span class="result-filename">{result['filename']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Original", f"{result['stats']['original_count']:,}")
                col2.metric("Cleaned", f"{result['stats']['final_count']:,}")
                col3.metric("Removed", f"{result['stats']['total_removed']:,}")
                col4.metric("Retention", f"{result['stats']['retention_rate']}%")
                
                with st.expander("📋 View Details"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Removal Breakdown**")
                        for key, value in result['removed'].items():
                            st.caption(f"• {key.replace('_', ' ').title()}: {value:,}")
                    
                    with detail_col2:
                        st.markdown("**Sample Preview**")
                        st.dataframe(result['preview'].head(5), use_container_width=True, height=200)
                
                with st.expander("💾 Download Options"):
                    cleaned_df = result['cleaned_df']
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_name = result['filename'].rsplit('.', 1)[0]
                    platform_prefix = result['platform'].lower().replace(' ', '_')
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            cleaned_df.to_excel(writer, index=False)
                        excel_data = output.getvalue()
                        
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"{platform_prefix}_{base_name}_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key=f"excel_{idx}"
                        )
                    
                    with col2:
                        csv_data = ('\ufeff' + cleaned_df.to_csv(index=False)).encode('utf-8')
                        
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name=f"{platform_prefix}_{base_name}_{timestamp}.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key=f"csv_{idx}"
                        )
                
                st.markdown("---")
        
        if st.button("🔄 Process New Files", use_container_width=True):
            st.session_state.cleaned_results = []
            st.session_state.processing_complete = False
            st.rerun()
    
    else:
        st.info("No results yet. Upload and process files in the first tab.")
