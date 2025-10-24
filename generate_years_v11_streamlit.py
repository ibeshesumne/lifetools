#!/usr/bin/env python3
"""
Streamlit app to generate a CSV file containing years from birth year to age 100,
with each year split into four seasons, and each season split into months.
Starts from the user's birth month and continues chronologically.
Includes Japanese reign period (era), Chinese zodiac, and Western zodiac for each month.
Shows preview of first and last rows.
"""

import streamlit as st
import csv
import re
import io


def get_japanese_era(year, month):
    """
    Returns the Japanese era name and reign year based on the year and month.
    Format: "Era Name Year" (e.g., "Showa 38", "Heisei 1")
    Modern eras: Meiji, Taisho, Showa, Heisei, Reiwa
    """
    month_num = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    m = month_num[month]
    
    # Modern Japanese eras with exact dates and reign years
    if year < 1868:
        return "Pre-Meiji"
    elif year == 1868:
        if m < 9:
            return "Pre-Meiji"
        else:
            return "Meiji 1"
    elif year <= 1911:
        era_year = year - 1867
        return f"Meiji {era_year}"
    elif year == 1912:
        if m <= 7:
            era_year = year - 1867
            return f"Meiji {era_year}"
        else:
            return "Taisho 1"
    elif year <= 1925:
        era_year = year - 1911
        return f"Taisho {era_year}"
    elif year == 1926:
        if m <= 12:
            era_year = year - 1911
            return f"Taisho {era_year}"
        else:
            return "Showa 1"
    elif year <= 1988:
        era_year = year - 1925
        return f"Showa {era_year}"
    elif year == 1989:
        if m <= 1:
            era_year = year - 1925
            return f"Showa {era_year}"
        else:
            return "Heisei 1"
    elif year <= 2018:
        era_year = year - 1988
        return f"Heisei {era_year}"
    elif year == 2019:
        if m <= 4:
            era_year = year - 1988
            return f"Heisei {era_year}"
        else:
            return "Reiwa 1"
    else:
        era_year = year - 2018
        return f"Reiwa {era_year}"


def get_chinese_zodiac(year, month):
    """
    Returns the Chinese zodiac animal based on the year and month.
    """
    zodiac_animals = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake',
                      'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Wild Boar']
    
    zodiac_index = (year - 1900) % 12
    zodiac_animal = zodiac_animals[zodiac_index]
    zodiac_year = zodiac_index + 1
    
    return f"{zodiac_animal} Year {zodiac_year}"


def get_western_zodiac(month):
    """
    Returns the Western zodiac sign based on the month.
    """
    western_zodiac = {
        'January': 'Capricorn/Aquarius',
        'February': 'Aquarius/Pisces',
        'March': 'Pisces/Aries',
        'April': 'Aries/Taurus',
        'May': 'Taurus/Gemini',
        'June': 'Gemini/Cancer',
        'July': 'Cancer/Leo',
        'August': 'Leo/Virgo',
        'September': 'Virgo/Libra',
        'October': 'Libra/Scorpio',
        'November': 'Scorpio/Sagittarius',
        'December': 'Sagittarius/Capricorn'
    }
    
    return western_zodiac.get(month, 'Unknown')


def generate_csv(name, birth_year, birth_month):
    """
    Generates CSV data in memory and returns it as a string along with row data for preview.
    """
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name).lower()
    end_year = birth_year + 100
    
    season_map = {
        'January': 'winter',
        'February': 'winter',
        'March': 'spring',
        'April': 'spring',
        'May': 'spring',
        'June': 'summer',
        'July': 'summer',
        'August': 'summer',
        'September': 'autumn',
        'October': 'autumn',
        'November': 'autumn',
        'December': 'winter',
    }
    
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    birth_month_index = months.index(birth_month)
    rotated_months = months[birth_month_index:] + months[:birth_month_index]
    
    # Store all rows for preview
    all_rows = []
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Year', 'Age', 'Season', 'Month', 'Japanese Era', 'Chinese Zodiac', 'Western Zodiac'])
    all_rows.append(['Year', 'Age', 'Season', 'Month', 'Japanese Era', 'Chinese Zodiac', 'Western Zodiac'])
    
    current_year = birth_year
    month_count = 0
    total_months = (end_year - birth_year + 1) * 12
    
    while month_count < total_months:
        years_passed = month_count // 12
        age = years_passed
        
        month_index = month_count % 12
        month = rotated_months[month_index]
        season = season_map[month]
        
        japanese_era = get_japanese_era(current_year, month)
        chinese_zodiac = get_chinese_zodiac(current_year, month)
        western_zodiac = get_western_zodiac(month)
        
        row = [current_year, age, season, month, japanese_era, chinese_zodiac, western_zodiac]
        writer.writerow(row)
        all_rows.append(row)
        
        if month == 'December':
            current_year += 1
        
        month_count += 1
    
    csv_data = output.getvalue()
    output.close()
    
    return csv_data, sanitized_name, all_rows


def main():
    st.set_page_config(page_title="Life Chronology Generator", page_icon="📅", layout="wide")
    
    st.title("📅 Life Chronology Generator")
    st.markdown("Generate a comprehensive chronology from your birth to age 100")
    
    st.markdown("---")
    
    # User inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name = st.text_input("**Enter your name:**", placeholder="e.g., Michael")
    
    with col2:
        birth_year = st.number_input("**Enter your birth year:**", min_value=1868, max_value=2100, value=1990, step=1)
    
    with col3:
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        birth_month = st.selectbox("**Select your birth month:**", months)
    
    st.markdown("---")
    
    # Generate button
    if st.button("🚀 Generate Chronology", type="primary", use_container_width=True):
        if not name:
            st.error("⚠️ Please enter your name")
        else:
            with st.spinner("Generating your chronology..."):
                csv_data, sanitized_name, all_rows = generate_csv(name, birth_year, birth_month)
                
                st.success(f"✅ Chronology generated successfully for **{name}**!")
                
                # Show stats
                end_year = birth_year + 100
                total_rows = len(all_rows) - 1  # Exclude header
                st.info(f"📊 **Total years:** {end_year - birth_year + 1} | **Total rows:** {total_rows}")
                
                st.markdown("---")
                
                # Preview section
                st.markdown("### 📋 Preview")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**First 10 rows:**")
                    # Show first 10 rows (including header + 9 data rows)
                    preview_first = all_rows[:11]
                    for i, row in enumerate(preview_first):
                        if i == 0:
                            st.markdown(f"`{', '.join(map(str, row))}`")
                        else:
                            st.markdown(f"`{', '.join(map(str, row))}`")
                    st.markdown("...")
                
                with col2:
                    st.markdown("**Last 10 rows:**")
                    st.markdown("...")
                    # Show last 10 rows
                    preview_last = all_rows[-10:]
                    for i, row in enumerate(preview_last):
                        st.markdown(f"`{', '.join(map(str, row))}`")
                
                st.markdown("---")
                
                # Download button
                filename = f"{sanitized_name}_chronology.csv"
                st.download_button(
                    label="📥 Download Full CSV File",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # Information section
    with st.expander("ℹ️ About this tool"):
        st.markdown("""
        This tool generates a comprehensive life chronology CSV file that includes:
        
        - **Years**: From your birth year to age 100
        - **Age**: Your age for each month
        - **Seasons**: Winter, Spring, Summer, Autumn
        - **Months**: Starting from your birth month
        - **Japanese Era**: Modern Japanese reign periods (Meiji, Taisho, Showa, Heisei, Reiwa)
        - **Chinese Zodiac**: 12-year cycle with animals (Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Wild Boar)
        - **Western Zodiac**: Astrological signs for each month
        
        The chronology follows the 12-month cycle starting from your birth month, ensuring ages increment correctly on your birthday anniversary.
        """)


if __name__ == "__main__":
    main()

