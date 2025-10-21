import streamlit as st
import pandas as pd
import re
import emoji
import io
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Social Media Comment Cleaner",
    page_icon="🧹",
    layout="wide"
)

# Initialize session state
if 'cleaned_results' not in st.session_state:
    st.session_state.cleaned_results = []
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .platform-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.2rem;
    }
    .badge-instagram { background-color: #E1306C; color: white; }
    .badge-youtube { background-color: #FF0000; color: white; }
    .badge-tiktok { background-color: #000000; color: white; }
    .badge-reddit { background-color: #FF4500; color: white; }
    .badge-facebook { background-color: #1877F2; color: white; }
    .badge-other { background-color: #6c757d; color: white; }
    </style>
""", unsafe_allow_html=True)

class CommentCleaner:
    """Social media comment cleaning engine"""
    
    def __init__(self, min_char_length=10):
        self.min_char_length = min_char_length
        self.cleaning_stats = {}
        self.removed_rows = {
            'blank_empty': 0,
            'too_short': 0,
            'only_special_chars': 0,
            'only_emojis': 0
        }
        
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
        return re.sub(url_pattern, '', text)
    
    def remove_mentions(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        return re.sub(r'@\w+', '', text)
    
    def remove_hashtags(self, text):
        if pd.isna(text):
            return text
        text = str(text)
        return re.sub(r'#\w+', '', text)
    
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
    
    def is_valid_comment(self, text, min_length):
        if pd.isna(text) or text == '':
            self.removed_rows['blank_empty'] += 1
            return False
        
        cleaned = str(text).strip()
        
        if cleaned == '':
            self.removed_rows['blank_empty'] += 1
            return False
        
        if len(cleaned) < min_length:
            self.removed_rows['too_short'] += 1
            return False
        
        if re.match(r'^[^a-zA-Z]+$', cleaned):
            self.removed_rows['only_special_chars'] += 1
            return False
            
        return True
    
    def detect_comment_column(self, df):
        columns_lower = [col.lower() for col in df.columns]
        
        if 'text' in columns_lower:
            idx = columns_lower.index('text')
            return df.columns[idx]
        elif 'comment' in columns_lower:
            idx = columns_lower.index('comment')
            return df.columns[idx]
        else:
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
        df['word_count'] = df['cleaned_comment'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
        
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

# Header
st.markdown('<div class="main-header">🧹 Social Media Comment Cleaner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Clean and process comments from multiple platforms simultaneously</div>', unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.header("⚙️ Cleaning Settings")

min_length = st.sidebar.slider(
    "Minimum Character Length",
    min_value=5,
    max_value=50,
    value=10,
    help="Comments shorter than this will be removed"
)

st.sidebar.subheader("Remove Elements")
remove_emoji = st.sidebar.checkbox(
    "Remove emoji-only comments", 
    value=True,
    help="Removes comments containing ONLY emojis (e.g., '😂😂😂'). Keeps comments with text + emojis."
)
remove_url = st.sidebar.checkbox("Remove URLs", value=True)
remove_mention = st.sidebar.checkbox("Remove @Mentions", value=False)
remove_hashtag = st.sidebar.checkbox("Remove #Hashtags", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📦 Export Options")
split_files = st.sidebar.checkbox(
    "Split large files (>10k rows)",
    value=True,
    help="Split files larger than 10,000 rows into multiple downloads"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Platform Averages")
st.sidebar.markdown("""
- **YouTube**: 70-75% retention
- **Instagram**: 65-70% retention
- **TikTok**: 55-65% retention
- **Reddit**: 75-82% retention
- **Facebook**: 60-68% retention
""")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Your Files")
    uploaded_files = st.file_uploader(
        "Choose CSV or Excel files (you can select multiple files)",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        help="Upload one or more comment datasets. Select multiple files to process different platforms together."
    )

with col2:
    st.subheader("ℹ️ Quick Guide")
    st.markdown("""
    1. Upload one or more files
    2. Label each file (e.g., Instagram, YouTube)
    3. Adjust settings in sidebar
    4. Click 'Clean All Data'
    5. Download cleaned files
    """)

if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} file(s) uploaded")
    
    # Platform selection for each file
    st.subheader("🏷️ Label Your Files")
    st.markdown("Assign a platform name to each file for easier identification:")
    
    file_platforms = {}
    cols = st.columns(min(len(uploaded_files), 3))
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with cols[idx % 3]:
            platform = st.selectbox(
                f"{uploaded_file.name}",
                ["Instagram", "YouTube", "TikTok", "Reddit", "Facebook", "Twitter", "LinkedIn", "Other"],
                key=f"platform_{idx}",
                index=0
            )
            file_platforms[uploaded_file.name] = platform
    
    # Clean button
    if st.button("🧹 Clean All Data", type="primary", use_container_width=True):
        st.session_state.cleaned_results = []
        st.session_state.processing_complete = False
        
        with st.spinner(f"Cleaning {len(uploaded_files)} file(s)... This may take a moment."):
            
            for uploaded_file in uploaded_files:
                try:
                    file_extension = uploaded_file.name.lower().split('.')[-1]
                    
                    if file_extension == 'csv':
                        df = pd.read_csv(uploaded_file, encoding='utf-8', encoding_errors='ignore')
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
                    
                    # Store results
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
            
            st.session_state.processing_complete = True
        
        st.success(f"✓ Cleaned {len(st.session_state.cleaned_results)} file(s) successfully!")
        st.rerun()

# Display results if processing is complete
if st.session_state.processing_complete and st.session_state.cleaned_results:
    
    st.markdown("---")
    st.header("📊 Cleaning Results")
    
    # Summary metrics
    total_original = sum(r['stats']['original_count'] for r in st.session_state.cleaned_results)
    total_cleaned = sum(r['stats']['final_count'] for r in st.session_state.cleaned_results)
    total_removed = total_original - total_cleaned
    overall_retention = round((total_cleaned / total_original) * 100, 2) if total_original > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Original", f"{total_original:,}")
    with col2:
        st.metric("Total Cleaned", f"{total_cleaned:,}")
    with col3:
        st.metric("Total Removed", f"{total_removed:,}")
    with col4:
        st.metric("Overall Retention", f"{overall_retention}%")
    
    st.markdown("---")
    
    # Individual file results
    for idx, result in enumerate(st.session_state.cleaned_results):
        platform_class = result['platform'].lower().replace(' ', '-')
        
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
            <h3>
                <span class='platform-badge badge-{platform_class}'>{result['platform']}</span>
                {result['filename']}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats for this file
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Original", f"{result['stats']['original_count']:,}")
        with col2:
            st.metric("Cleaned", f"{result['stats']['final_count']:,}")
        with col3:
            st.metric("Removed", f"{result['stats']['total_removed']:,}")
        with col4:
            st.metric("Retention", f"{result['stats']['retention_rate']}%")
        
        # Detailed breakdown
        with st.expander(f"🔍 Detailed Breakdown - {result['filename']}"):
            breakdown_col1, breakdown_col2 = st.columns(2)
            
            with breakdown_col1:
                st.markdown("**Removed by Category:**")
                st.write(f"• Blank/Empty: {result['removed']['blank_empty']:,}")
                st.write(f"• Emoji-only: {result['removed']['only_emojis']:,}")
            
            with breakdown_col2:
                st.write(f"• Too Short: {result['removed']['too_short']:,}")
                st.write(f"• Special Chars Only: {result['removed']['only_special_chars']:,}")
        
        # Preview
        with st.expander(f"👀 Preview - {result['filename']}"):
            st.dataframe(result['preview'].head(10), use_container_width=True)
        
        # Download section
        st.subheader(f"💾 Download - {result['platform']}")
        
        cleaned_df = result['cleaned_df']
        CHUNK_SIZE = 10000
        total_rows = len(cleaned_df)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = result['filename'].rsplit('.', 1)[0]
        platform_prefix = result['platform'].lower().replace(' ', '_')
        
        if total_rows > CHUNK_SIZE and split_files:
            num_files = (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE > 0 else 0)
            
            st.info(f"📦 {total_rows:,} rows will be split into {num_files} files")
            
            download_cols = st.columns(min(num_files, 4))
            
            for i in range(num_files):
                with download_cols[i % 4]:
                    start_idx = i * CHUNK_SIZE
                    end_idx = min((i + 1) * CHUNK_SIZE, total_rows)
                    chunk_df = cleaned_df.iloc[start_idx:end_idx]
                    
                    st.write(f"**Part {i+1}:** {len(chunk_df):,} rows")
                    
                    # Excel download
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
            if total_rows > CHUNK_SIZE and not split_files:
                st.info(f"ℹ️ Downloading all {total_rows:,} rows in one file")
            
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
                csv_data = cleaned_df.to_csv(index=False).encode('utf-8')
                csv_filename = f"{platform_prefix}_{base_name}_{timestamp}.csv"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv",
                    use_container_width=True,
                    key=f"csv_single_{idx}"
                )
        
        st.markdown("---")
    
    # Clear results button
    if st.button("🔄 Process New Files", use_container_width=True):
        st.session_state.cleaned_results = []
        st.session_state.processing_complete = False
        st.rerun()

else:
    st.info("👆 Upload one or more files to get started")
    
    with st.expander("💡 Multi-Platform Processing"):
        st.markdown("""
        **Upload multiple files at once:**
        
        1. Click "Browse files" and select multiple CSV/Excel files
        2. Label each file with its platform (Instagram, YouTube, etc.)
        3. Click "Clean All Data" to process everything together
        4. Download separate cleaned files for each platform
        
        **Example:**
        - Upload: `instagram_comments.csv` (label: Instagram)
        - Upload: `youtube_comments.xlsx` (label: YouTube)
        - Upload: `tiktok_data.csv` (label: TikTok)
        
        **You'll get:**
        - `instagram_instagram_comments_20241021.xlsx`
        - `youtube_youtube_comments_20241021.xlsx`
        - `tiktok_tiktok_data_20241021.xlsx`
        
        All processed with the same settings, ready to analyze!
        """)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Made for internal team use • Data processed locally • Not stored</div>",
    unsafe_allow_html=True
)
