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
    .stats-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
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
        
        # Remove emoji-only comments if enabled
        if remove_emoji:
            emoji_only_mask = df[comment_column].apply(self.is_only_emojis)
            emoji_only_count = emoji_only_mask.sum()
            self.removed_rows['only_emojis'] = emoji_only_count
            df = df[~emoji_only_mask].copy()
        
        df['cleaned_comment'] = df[comment_column].copy()
        
        # DO NOT strip emojis from comments - only remove emoji-only comments above
        # Remove URLs, mentions, hashtags as configured
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
        
        # Store preview data without char_count and word_count
        self.preview_data = df_cleaned[['cleaned_comment']].copy()
        
        df_cleaned[original_comment_col] = df_cleaned['cleaned_comment']
        df_cleaned = df_cleaned.drop(['cleaned_comment', 'char_count', 'word_count'], axis=1)
        
        return df_cleaned, None

# Header
st.markdown('<div class="main-header">🧹 Social Media Comment Cleaner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Clean and process comments from Instagram, YouTube, TikTok, Reddit, and Facebook</div>', unsafe_allow_html=True)

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
    st.subheader("📤 Upload Your File")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your comment dataset (CSV or Excel format)"
    )

with col2:
    st.subheader("ℹ️ Quick Guide")
    st.markdown("""
    1. Upload CSV/Excel file
    2. Adjust settings in sidebar
    3. Click 'Clean Data'
    4. Download cleaned file
    """)

if uploaded_file is not None:
    try:
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file, encoding='utf-8', encoding_errors='ignore')
            file_type = "CSV"
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else None)
            file_type = "Excel"
        else:
            st.error(f"Unsupported file format: .{file_extension}")
            st.stop()
        
        st.success(f"✓ {file_type} file loaded: {uploaded_file.name}")
        
        with st.expander("📋 View Original Data Info"):
            st.write(f"**Total Rows:** {len(df):,}")
            st.write(f"**Columns:** {', '.join(df.columns)}")
            st.dataframe(df.head(5), use_container_width=True)
        
        st.subheader("🎯 Select Comment Column")
        
        cleaner = CommentCleaner(min_char_length=min_length)
        detected_col = cleaner.detect_comment_column(df)
        
        if detected_col:
            st.info(f"Auto-detected column: **{detected_col}**")
            comment_column = st.selectbox(
                "Comment Column",
                options=df.columns,
                index=list(df.columns).index(detected_col)
            )
        else:
            st.warning("Could not auto-detect comment column. Please select manually.")
            comment_column = st.selectbox("Comment Column", options=df.columns)
        
        if st.button("🧹 Clean Data", type="primary", use_container_width=True):
            with st.spinner("Cleaning data... This may take a moment for large files."):
                
                cleaned_df, error = cleaner.clean_dataset(
                    df,
                    comment_column=comment_column,
                    remove_emoji=remove_emoji,
                    remove_url=remove_url,
                    remove_mention=remove_mention,
                    remove_hashtag=remove_hashtag,
                    min_length=min_length
                )
                
                if error:
                    st.error(error)
                else:
                    st.success("✓ Cleaning complete!")
                    
                    st.subheader("📊 Cleaning Results")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Original", f"{cleaner.cleaning_stats['original_count']:,}")
                    
                    with col2:
                        st.metric("Cleaned", f"{cleaner.cleaning_stats['final_count']:,}")
                    
                    with col3:
                        st.metric("Removed", f"{cleaner.cleaning_stats['total_removed']:,}")
                    
                    with col4:
                        st.metric("Retention", f"{cleaner.cleaning_stats['retention_rate']}%")
                    
                    with st.expander("🔍 Detailed Breakdown"):
                        breakdown_col1, breakdown_col2 = st.columns(2)
                        
                        with breakdown_col1:
                            st.markdown("**Removed by Category:**")
                            st.write(f"• Blank/Empty: {cleaner.removed_rows['blank_empty']:,}")
                            st.write(f"• Emoji-only: {cleaner.removed_rows['only_emojis']:,}")
                        
                        with breakdown_col2:
                            st.write(f"• Too Short: {cleaner.removed_rows['too_short']:,}")
                            st.write(f"• Special Chars Only: {cleaner.removed_rows['only_special_chars']:,}")
                    
                    st.subheader("👀 Preview Cleaned Data")
                    st.dataframe(
                        cleaner.preview_data.head(20),
                        use_container_width=True
                    )
                    
                    st.subheader("📋 Final Output Columns")
                    st.write(", ".join(cleaned_df.columns))
                    st.info("ℹ️ Note: Original comment column replaced with cleaned version. Emojis are preserved in comments with text.")
                    
                    st.subheader("💾 Download Cleaned Data")
                    
                    CHUNK_SIZE = 10000
                    total_rows = len(cleaned_df)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Check if we need to split AND if user wants splitting
                    if total_rows > CHUNK_SIZE and split_files:
                        num_files = (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE > 0 else 0)
                        
                        st.info(f"📦 Large dataset: {total_rows:,} rows will be split into {num_files} files ({CHUNK_SIZE:,} rows each)")
                        
                        tabs = st.tabs([f"Part {i+1}" for i in range(num_files)])
                        
                        for i, tab in enumerate(tabs):
                            with tab:
                                start_idx = i * CHUNK_SIZE
                                end_idx = min((i + 1) * CHUNK_SIZE, total_rows)
                                chunk_df = cleaned_df.iloc[start_idx:end_idx]
                                
                                st.write(f"**Rows:** {len(chunk_df):,} (rows {start_idx+1:,} to {end_idx:,})")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                        chunk_df.to_excel(writer, index=False)
                                    excel_data = output.getvalue()
                                    
                                    excel_filename = f"cleaned_comments_{timestamp}_part{i+1}.xlsx"
                                    
                                    st.download_button(
                                        label=f"📥 Download Part {i+1} (Excel)",
                                        data=excel_data,
                                        file_name=excel_filename,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True,
                                        key=f"excel_{i}"
                                    )
                                
                                with col2:
                                    csv_data = chunk_df.to_csv(index=False).encode('utf-8')
                                    csv_filename = f"cleaned_comments_{timestamp}_part{i+1}.csv"
                                    
                                    st.download_button(
                                        label=f"📥 Download Part {i+1} (CSV)",
                                        data=csv_data,
                                        file_name=csv_filename,
                                        mime="text/csv",
                                        use_container_width=True,
                                        key=f"csv_{i}"
                                    )
                    
                    else:
                        # Single file download
                        if total_rows > CHUNK_SIZE and not split_files:
                            st.info(f"ℹ️ Downloading all {total_rows:,} rows in a single file")
                        
                        download_col1, download_col2 = st.columns(2)
                        
                        with download_col1:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                cleaned_df.to_excel(writer, index=False)
                            excel_data = output.getvalue()
                            
                            excel_filename = f"cleaned_comments_{timestamp}.xlsx"
                            
                            st.download_button(
                                label="📥 Download as Excel",
                                data=excel_data,
                                file_name=excel_filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        
                        with download_col2:
                            csv_data = cleaned_df.to_csv(index=False).encode('utf-8')
                            csv_filename = f"cleaned_comments_{timestamp}.csv"
                            
                            st.download_button(
                                label="📥 Download as CSV",
                                data=csv_data,
                                file_name=csv_filename,
                                mime="text/csv",
                                use_container_width=True
                            )
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Make sure your file is a valid CSV or Excel file with proper encoding.")

else:
    st.info("👆 Upload a CSV or Excel file to get started")
    
    with st.expander("💡 Example File Format"):
        st.markdown("""
        Your file (CSV or Excel) should have a column named either **'text'** or **'comment'** containing the comments:
        
        | text | username | date |
        |------|----------|------|
        | Great video! 👍 | user123 | 2024-01-15 |
        | First comment!! | user456 | 2024-01-15 |
        | Check this link http://spam.com | bot789 | 2024-01-15 |
        
        **Supported formats:**
        - CSV files (.csv)
        - Excel files (.xlsx, .xls)
        
        Other columns will be preserved in the output.
        """)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Made for internal team use • Data processed locally • Not stored</div>",
    unsafe_allow_html=True
)
