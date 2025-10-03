# ============================================================
# CELL 1: Install Required Libraries
# ============================================================
# Run this first - it will take 10-15 seconds

!pip install emoji openpyxl -q

print("✓ Libraries installed successfully")


# ============================================================
# CELL 2: Import Libraries
# ============================================================

import pandas as pd
import re
import emoji
from google.colab import files
import io

print("✓ All imports loaded")


# ============================================================
# CELL 3: Define CommentCleaner Class
# ============================================================

class CommentCleaner:
    """
    Cell-by-cell cleaning toolkit for social media comment datasets
    Handles IG, YT, TT, Reddit, and FB comment exports
    Auto-detects 'text' or 'comment' columns
    """
    
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
        """Remove all emoji characters"""
        if pd.isna(text):
            return text
        text = str(text)  # Convert to string
        return emoji.replace_emoji(text, replace='')
    
    def remove_urls(self, text):
        """Remove URLs and web links"""
        if pd.isna(text):
            return text
        text = str(text)  # Convert to string
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    def remove_mentions(self, text):
        """Remove @ mentions"""
        if pd.isna(text):
            return text
        text = str(text)  # Convert to string
        return re.sub(r'@\w+', '', text)
    
    def remove_hashtags(self, text):
        """Remove # hashtags"""
        if pd.isna(text):
            return text
        text = str(text)  # Convert to string
        return re.sub(r'#\w+', '', text)
    
    def clean_whitespace(self, text):
        """Normalize excessive whitespace"""
        if pd.isna(text):
            return text
        text = str(text)  # Convert to string
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_special_chars(self, text):
        """Remove excessive special characters and repetitive punctuation"""
        if pd.isna(text):
            return text
        text = str(text)  # Convert to string
        text = re.sub(r'([!?.]){3,}', r'\1', text)
        return text
    
    def is_blank_or_empty(self, text):
        """Check if cell is blank, empty, or whitespace only"""
        if pd.isna(text):
            return True
        if text == '':
            return True
        if str(text).strip() == '':
            return True
        return False
    
    def is_only_emojis(self, text):
        """Check if text contains only emojis"""
        if pd.isna(text):
            return False
        no_emoji = emoji.replace_emoji(str(text), replace='')
        return no_emoji.strip() == ''
    
    def is_valid_comment(self, text, min_length):
        """Check if comment meets minimum quality standards"""
        if pd.isna(text) or text == '':
            self.removed_rows['blank_empty'] += 1
            return False
        
        cleaned = text.strip()
        
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
        """Auto-detect if column is 'text' or 'comment'"""
        columns_lower = [col.lower() for col in df.columns]
        
        if 'text' in columns_lower:
            idx = columns_lower.index('text')
            return df.columns[idx]
        elif 'comment' in columns_lower:
            idx = columns_lower.index('comment')
            return df.columns[idx]
        else:
            print("\n⚠ Could not find 'text' or 'comment' column")
            print(f"Available columns: {list(df.columns)}")
            return None
    
    def clean_dataset(self, df, comment_column=None, 
                     remove_emoji=True, 
                     remove_url=True,
                     remove_mention=False,
                     remove_hashtag=False,
                     min_length=None):
        """
        Cell-by-cell cleaning pipeline with blank removal
        """
        
        if comment_column is None:
            comment_column = self.detect_comment_column(df)
            if comment_column is None:
                raise ValueError("Could not auto-detect comment column. Please specify manually.")
            print(f"✓ Detected comment column: '{comment_column}'")
        
        if comment_column not in df.columns:
            raise ValueError(f"Column '{comment_column}' not found in dataset")
        
        if min_length is None:
            min_length = self.min_char_length
        
        original_count = len(df)
        original_comment_col = comment_column  # Store original column name
        
        self.removed_rows = {
            'blank_empty': 0,
            'too_short': 0,
            'only_special_chars': 0,
            'only_emojis': 0
        }
        
        print("\n→ Removing blank/empty cells...")
        df = df[~df[comment_column].apply(self.is_blank_or_empty)].copy()
        blanks_removed = original_count - len(df)
        print(f"  Removed {blanks_removed:,} blank rows")
        
        if remove_emoji:
            print("→ Checking for emoji-only comments...")
            emoji_only_mask = df[comment_column].apply(self.is_only_emojis)
            emoji_only_count = emoji_only_mask.sum()
            self.removed_rows['only_emojis'] = emoji_only_count
            df = df[~emoji_only_mask].copy()
            print(f"  Removed {emoji_only_count:,} emoji-only comments")
        
        print("→ Processing each cell...")
        df['cleaned_comment'] = df[comment_column].copy()
        
        if remove_emoji:
            df['cleaned_comment'] = df['cleaned_comment'].apply(self.remove_emojis)
        
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
        
        print("→ Applying quality filters...")
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
        
        # Prepare final output: Replace original column with cleaned, remove metrics
        df_cleaned[original_comment_col] = df_cleaned['cleaned_comment']
        df_cleaned = df_cleaned.drop(['cleaned_comment', 'char_count', 'word_count'], axis=1)
        
        return df_cleaned
    
    def print_stats(self):
        """Display detailed cleaning statistics"""
        print("\n" + "="*60)
        print("CLEANING RESULTS - DETAILED BREAKDOWN")
        print("="*60)
        print(f"Original comments:          {self.cleaning_stats['original_count']:>10,}")
        print(f"After blank removal:        {self.cleaning_stats['after_blank_removal']:>10,}")
        print("-" * 60)
        print("Removed by category:")
        print(f"  • Blank/empty cells:      {self.removed_rows['blank_empty']:>10,}")
        print(f"  • Emoji-only:             {self.removed_rows['only_emojis']:>10,}")
        print(f"  • Too short:              {self.removed_rows['too_short']:>10,}")
        print(f"  • Only special chars:     {self.removed_rows['only_special_chars']:>10,}")
        print("-" * 60)
        print(f"Final cleaned comments:     {self.cleaning_stats['final_count']:>10,}")
        print(f"Total removed:              {self.cleaning_stats['total_removed']:>10,}")
        print(f"Retention rate:             {self.cleaning_stats['retention_rate']:>9.1f}%")
        print("="*60 + "\n")

print("✓ CommentCleaner class defined")


# ============================================================
# CELL 4: Upload Your CSV or Excel File
# ============================================================

print("="*60)
print("UPLOAD YOUR FILE")
print("="*60)
print("\nSupported formats: CSV (.csv) and Excel (.xlsx, .xls)")
print("Click 'Choose Files' and select your file")
print("Supports: Instagram, YouTube, TikTok, Reddit, Facebook exports\n")

uploaded = files.upload()

filename = list(uploaded.keys())[0]
print(f"\n✓ File uploaded: {filename}")


# ============================================================
# CELL 5: Load and Inspect Data
# ============================================================

# Detect file type and load accordingly
file_extension = filename.lower().split('.')[-1]

print("="*60)
print("LOADING FILE")
print("="*60)
print(f"File type detected: {file_extension.upper()}")

try:
    if file_extension == 'csv':
        # Load CSV file
        df = pd.read_csv(io.BytesIO(uploaded[filename]), encoding='utf-8', encoding_errors='ignore')
        print("✓ CSV file loaded successfully")
    elif file_extension in ['xlsx', 'xls']:
        # Load Excel file
        df = pd.read_excel(io.BytesIO(uploaded[filename]), engine='openpyxl' if file_extension == 'xlsx' else None)
        print("✓ Excel file loaded successfully")
    else:
        raise ValueError(f"Unsupported file format: .{file_extension}")
        
except Exception as e:
    print(f"❌ Error loading file: {str(e)}")
    print("Please ensure your file is a valid CSV or Excel file.")
    raise

print("="*60)
print("FILE INSPECTION")
print("="*60)
print(f"\nTotal rows loaded: {len(df):,}")
print(f"\nColumns in your file:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Show first few rows
print("\n" + "-"*60)
print("First 3 rows preview:")
print("-"*60)
print(df.head(3))

# Check for blank values
print("\n" + "-"*60)
print("Blank/null value check:")
print("-"*60)
null_counts = df.isnull().sum()
for col in df.columns:
    if null_counts[col] > 0:
        print(f"  {col}: {null_counts[col]:,} blank cells")


# ============================================================
# CELL 6: Configure and Run Cleaning
# ============================================================
# EDIT THESE SETTINGS BEFORE RUNNING:

print("="*60)
print("STARTING CLEANING PROCESS")
print("="*60)

# Initialize the cleaner
cleaner = CommentCleaner(min_char_length=10)  # Change minimum character count here

# Run the cleaning
cleaned_df = cleaner.clean_dataset(
    df, 
    comment_column=None,      # Auto-detects 'text' or 'comment' - or specify: 'your_column_name'
    remove_emoji=True,        # Set to False to keep emojis
    remove_url=True,          # Set to False to keep URLs
    remove_mention=False,     # Set to True to remove @mentions
    remove_hashtag=False,     # Set to True to remove #hashtags
    min_length=10             # Minimum characters after cleaning (change as needed)
)

# Display results
cleaner.print_stats()

# Ask user about file splitting preference
print("\n" + "="*60)
print("EXPORT OPTIONS")
print("="*60)
if len(cleaned_df) > 10000:
    print(f"\nYour cleaned dataset has {len(cleaned_df):,} rows.")
    print("Would you like to:")
    print("  1. Split into multiple files (10,000 rows each)")
    print("  2. Download as single file (all rows)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    SPLIT_FILES = (choice == "1")
else:
    SPLIT_FILES = False  # No need to ask if file is small


# ============================================================
# CELL 7: Preview Cleaned Data
# ============================================================

print("="*60)
print("CLEANED DATA PREVIEW")
print("="*60)

# Show sample of cleaned comments
print("\nFirst 10 cleaned rows:")
print("-"*60)
print(cleaned_df.head(10).to_string(index=False))

print("\n" + "-"*60)
print("Final columns in output:")
print("-"*60)
for col in cleaned_df.columns:
    print(f"  • {col}")


# ============================================================
# CELL 8: Export and Download (with Optional Auto-Split)
# ============================================================

print("="*60)
print("EXPORTING CLEANED DATA")
print("="*60)

CHUNK_SIZE = 10000  # Split into files of 10,000 rows each

total_rows = len(cleaned_df)

# Create base filename (remove original extension)
base_filename = '.'.join(filename.split('.')[:-1]) + '_cleaned'

# Check if we need to split AND if user wants splitting
if total_rows > CHUNK_SIZE and SPLIT_FILES:
    num_files = (total_rows // CHUNK_SIZE) + (1 if total_rows % CHUNK_SIZE > 0 else 0)
    
    print(f"\n📦 Splitting {total_rows:,} rows into {num_files} files ({CHUNK_SIZE:,} rows each)")
    print("-" * 60)
    
    exported_files = []
    
    for i in range(num_files):
        start_idx = i * CHUNK_SIZE
        end_idx = min((i + 1) * CHUNK_SIZE, total_rows)
        chunk_df = cleaned_df.iloc[start_idx:end_idx]
        
        # Create filename with part number (always export as Excel)
        part_filename = f"{base_filename}_part{i+1}.xlsx"
        chunk_df.to_excel(part_filename, index=False, engine='openpyxl')
        
        exported_files.append(part_filename)
        print(f"✓ Part {i+1}: {part_filename} ({len(chunk_df):,} rows)")
    
    print("-" * 60)
    print(f"✓ Total files created: {num_files}")
    print(f"✓ Total rows exported: {total_rows:,}")
    
    # Download all files
    print("\n" + "="*60)
    print("DOWNLOADING FILES...")
    print("="*60)
    
    for file in exported_files:
        files.download(file)
        print(f"✓ Downloaded: {file}")
    
else:
    # Single file export
    if total_rows > CHUNK_SIZE and not SPLIT_FILES:
        print(f"\nℹ️ Exporting all {total_rows:,} rows as single file")
    
    output_filename = f"{base_filename}.xlsx"
    cleaned_df.to_excel(output_filename, index=False, engine='openpyxl')
    
    print(f"\n✓ File exported: {output_filename}")
    print(f"✓ Total rows exported: {total_rows:,}")
    
    print("\n" + "="*60)
    print("DOWNLOADING FILE...")
    print("="*60)
    files.download(output_filename)
    print("✓ Download started!")

print(f"\nColumns in cleaned file(s):")
for col in cleaned_df.columns:
    print(f"  • {col}")

print("\n" + "="*60)
print("NOTE: Original comment column replaced with cleaned version")
print("Metric columns (char_count, word_count) removed from export")
print("All files exported as Excel (.xlsx) format")
print("="*60)

print("\n✓ Check your browser's download folder")
print("\n" + "="*60)
print("PROCESS COMPLETE")
print("="*60)
