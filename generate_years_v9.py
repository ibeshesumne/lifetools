#!/usr/bin/env python3
"""
Script to generate a CSV file containing years from birth year to age 100,
with each year split into four seasons, and each season split into months.
Starts from the user's birth month and continues chronologically.
Includes Japanese reign period (era), Chinese zodiac, and Western zodiac for each month.
Personalized with user's name in the filename.
"""

import csv
import re


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
        if m < 9:  # Before September (but Meiji started Jan 25)
            return "Pre-Meiji"
        else:
            return "Meiji 1"
    elif year <= 1911:
        era_year = year - 1867  # Meiji started in 1868
        return f"Meiji {era_year}"
    elif year == 1912:
        if m <= 7:
            era_year = year - 1867
            return f"Meiji {era_year}"
        else:
            return "Taisho 1"
    elif year <= 1925:
        era_year = year - 1911  # Taisho started in 1912
        return f"Taisho {era_year}"
    elif year == 1926:
        if m <= 12:
            era_year = year - 1911
            return f"Taisho {era_year}"
        else:
            return "Showa 1"
    elif year <= 1988:
        era_year = year - 1925  # Showa started in 1926
        return f"Showa {era_year}"
    elif year == 1989:
        if m <= 1:
            era_year = year - 1925
            return f"Showa {era_year}"
        else:
            return "Heisei 1"
    elif year <= 2018:
        era_year = year - 1988  # Heisei started in 1989
        return f"Heisei {era_year}"
    elif year == 2019:
        if m <= 4:
            era_year = year - 1988
            return f"Heisei {era_year}"
        else:
            return "Reiwa 1"
    else:
        era_year = year - 2018  # Reiwa started in 2019
        return f"Reiwa {era_year}"


def get_chinese_zodiac(year, month):
    """
    Returns the Chinese zodiac animal based on the year and month.
    The zodiac year typically starts at Chinese New Year (around Jan 21 - Feb 20).
    For simplicity, treats each Gregorian year as belonging to one zodiac animal.
    """
    # Chinese zodiac animals in order
    zodiac_animals = ['Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake',
                      'Horse', 'Goat', 'Monkey', 'Rooster', 'Dog', 'Wild Boar']
    
    # Chinese zodiac cycles every 12 years
    # Years for each animal: Rat (1900, 1912, 1924...), Ox (1901, 1913...), etc.
    zodiac_index = (year - 1900) % 12
    
    zodiac_animal = zodiac_animals[zodiac_index]
    
    # Calculate which year in the 12-year cycle (1-12)
    zodiac_year = zodiac_index + 1
    
    return f"{zodiac_animal} Year {zodiac_year}"


def get_western_zodiac(month):
    """
    Returns the Western zodiac sign based on the month.
    Since we only have month names (not specific dates), assigns the dominant sign for each month.
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


def main():
    # Ask user for name
    name = input("Enter your name: ").strip()
    
    if not name:
        print("Error: Name cannot be empty")
        return
    
    # Sanitize name for filename (remove special characters, spaces become underscores)
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name).lower()
    
    # Ask user for birth year
    try:
        birth_year = int(input("Enter your birth year: "))
    except ValueError:
        print("Error: Please enter a valid year (e.g., 1990)")
        return
    
    # Validate birth year (reasonable range)
    if birth_year < 1868 or birth_year > 2100:
        print("Warning: Birth year may be outside modern Japanese era system. Proceeding anyway...")
    
    # Ask user for birth month
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    print("\nAvailable months:")
    for i, month in enumerate(months, 1):
        print(f"  {i}. {month}")
    
    try:
        birth_month_num = int(input("\nEnter your birth month (1-12): "))
        if birth_month_num < 1 or birth_month_num > 12:
            print("Error: Month must be between 1 and 12")
            return
        birth_month = months[birth_month_num - 1]
    except ValueError:
        print("Error: Please enter a valid number (1-12)")
        return
    
    # Calculate end year (age 100)
    end_year = birth_year + 100
    
    # Prepare CSV filename with user's name
    csv_filename = f"{sanitized_name}_chronology.csv"
    
    # Define seasons with their months
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
    
    # Create a list of all months starting from birth month
    birth_month_index = months.index(birth_month)
    rotated_months = months[birth_month_index:] + months[:birth_month_index]
    
    # Generate years with seasons and months, then write to CSV
    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with Japanese Era, Chinese Zodiac, and Western Zodiac columns
            writer.writerow(['Year', 'Age', 'Season', 'Month', 'Japanese Era', 'Chinese Zodiac', 'Western Zodiac'])
            
            # Write each year from birth to age 100
            current_year = birth_year
            month_count = 0
            
            # Calculate total months from birth to age 100
            total_months = (end_year - birth_year + 1) * 12
            
            while month_count < total_months:
                # Calculate age based on how many full years have passed
                years_passed = month_count // 12
                age = years_passed
                
                # Determine which month we're on in the cycle
                month_index = month_count % 12
                month = rotated_months[month_index]
                season = season_map[month]
                
                # Get Japanese era for this month
                japanese_era = get_japanese_era(current_year, month)
                
                # Get Chinese zodiac for this month
                chinese_zodiac = get_chinese_zodiac(current_year, month)
                
                # Get Western zodiac for this month
                western_zodiac = get_western_zodiac(month)
                
                writer.writerow([current_year, age, season, month, japanese_era, chinese_zodiac, western_zodiac])
                
                # If we're at December, increment to next year
                if month == 'December':
                    current_year += 1
                
                month_count += 1
        
        total_rows = (end_year - birth_year + 1) * 12  # 12 months per year
        print(f"\nSuccessfully created CSV file: {csv_filename}")
        print(f"Hello {name}! Your chronology starting from {birth_month} {birth_year} to age 100 has been created.")
        print(f"Total years: {end_year - birth_year + 1}")
        print(f"Total rows: {total_rows} (including header)")
        print(f"Starting from: {birth_month} {birth_year}")
        print(f"Ending at: {months[(birth_month_index - 1) % 12]} {end_year}")
        print(f"\nJapanese Eras included (showing reign name and year):")
        print(f"  Meiji: 1868-1912 (e.g., Meiji 1, Meiji 2, ...)")
        print(f"  Taisho: 1912-1926 (e.g., Taisho 1, Taisho 2, ...)")
        print(f"  Showa: 1926-1989 (e.g., Showa 1, Showa 2, Showa 38, ...)")
        print(f"  Heisei: 1989-2019 (e.g., Heisei 1, Heisei 2, ...)")
        print(f"  Reiwa: 2019-present (e.g., Reiwa 1, Reiwa 2, ...)")
        print(f"\nChinese Zodiac signs:")
        print(f"  Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Wild Boar")
        print(f"  Cycle repeats every 12 years")
        print(f"\nWestern Zodiac signs:")
        print(f"  Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces")
        print(f"  Shown as overlaps (e.g., Capricorn/Aquarius) since dates span multiple signs within each month")
        
    except Exception as e:
        print(f"Error creating CSV file: {e}")


if __name__ == "__main__":
    main()

