# Life Chronology Generator - Streamlit Apps

## Available Versions

### Version 12 (Latest - Recommended)
**File:** `generate_years_v12_streamlit.py`

- **Compact single-page design** - everything fits without scrolling
- **Prominent download button** - placed BEFORE the preview table
- Shows **first 5 rows** preview
- Shows **last 3 rows** up to present day
- Clear indication that CSV is ready for download
- Optimized for one-page viewing

### Version 11
**File:** `generate_years_v11_streamlit.py`

- Shows first 10 rows preview
- Shows last 5 rows up to present day
- Full CSV download option

### Version 10
**File:** `generate_years_v10_streamlit.py`

- Shows first 20 rows preview
- Full CSV download option

## How to Run

1. Install Streamlit (if not already installed):
```bash
pip install streamlit
```

2. Run the Streamlit app (choose one):
```bash
# Version 12 (recommended - compact single-page)
streamlit run generate_years_v12_streamlit.py

# Version 11
streamlit run generate_years_v11_streamlit.py

# Version 10
streamlit run generate_years_v10_streamlit.py
```

3. The app will open in your browser automatically

## Features

- **Interactive Web Interface**: Enter your name, birth year, and birth month
- **Download CSV**: Download the generated chronology file
- **Preview**: See abbreviated first and last rows before downloading
- **No File Cleanup Needed**: CSV is generated in memory and provided for download

## What's Included in the CSV

- Year, Age, Season, Month
- Japanese Era (with reign year)
- Chinese Zodiac (12-year cycle)
- Western Zodiac (monthly signs)

## Note

Since the CSV is generated in memory and provided as a download, there's no need to delete any files - everything is handled automatically!

