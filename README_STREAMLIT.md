# Life Chronology Generator - Streamlit Apps

## Available Versions

### Version 14 (Latest - Recommended) ⭐
**File:** `generate_years_v14_streamlit.py`

- **Dual Format Export** - Download both CSV and Excel files
- **Formatted Excel** - Spring months shaded green, Autumn months shaded light red
- **Side-by-side download buttons** - Easy access to both formats
- Shows **first 5 rows** preview
- Shows **last 3 rows** up to present day
- Compact single-page design
- CSV format for compatibility, Excel format for visual appeal

### Version 13
**File:** `generate_years_v13_streamlit.py`

- **Excel Export Only** - Downloads formatted XLSX file
- **Formatted Excel** - Spring months shaded green, Autumn months shaded light red
- Auto-adjusted column widths
- Shows **first 5 rows** preview
- Shows **last 3 rows** up to present day

### Version 12
**File:** `generate_years_v12_streamlit.py`

- **CSV Export Only** - Downloads CSV file
- Compact single-page design
- Shows **first 5 rows** preview
- Shows **last 3 rows** up to present day

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

1. Install required packages:
```bash
pip install streamlit openpyxl
```
or use the requirements file:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app (choose one):
```bash
# Version 14 (recommended - dual format export)
streamlit run generate_years_v14_streamlit.py

# Version 13 (Excel only with formatting)
streamlit run generate_years_v13_streamlit.py

# Version 12 (CSV only)
streamlit run generate_years_v12_streamlit.py

# Version 11
streamlit run generate_years_v11_streamlit.py

# Version 10
streamlit run generate_years_v10_streamlit.py
```

3. The app will open in your browser automatically at `http://localhost:8501`

## Features

- **Interactive Web Interface**: Enter your name, birth year, and birth month
- **Download Options**: Download CSV or Excel (XLSX) files
- **Formatted Excel** (v13 & v14): Spring months (Mar-May) shaded green, Autumn months (Sep-Nov) shaded light red
- **Dual Format Export** (v14): Download both CSV and Excel simultaneously
- **Preview**: See abbreviated first and last rows before downloading
- **No File Cleanup Needed**: Files are generated in memory and provided for download

## What's Included in the Files

Both CSV and Excel files contain:
- Year, Age, Season, Month
- Japanese Era (with reign year)
- Chinese Zodiac (12-year cycle)
- Western Zodiac (monthly signs)

**Excel Format (v13 & v14) additionally includes:**
- Visual formatting with colored rows
- Auto-adjusted column widths
- Bold headers

## Format Comparison

- **CSV**: Plain text format, compatible with all spreadsheet applications
- **Excel (XLSX)**: Formatted with colors for easier reading

## Note

All files are generated in memory and provided as downloads - no need to delete any files!

