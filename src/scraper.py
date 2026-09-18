from bs4 import BeautifulSoup
import time
import requests
import json
from pathlib import Path

def fetch_year(year):
    # Define a browser User-Agent header so Wikipedia doesn't block the script
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    time.sleep(1)
    try:
        response = requests.get(f'https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_{year}', headers=headers)
        return list(parse_year_page(response.text, year))
    except requests.RequestException as e:
        print(f"Error fetching year {year}: {e}")
        return None



def parse_year_page(html, year):
    # takes the raw html and a year and returns a list of dictionaries with the rank, title, and artist
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    for row in table.find_all('tr')[1:]:
        rank = row.find_all('td')[0].text.strip()
        title = row.find_all('td')[1].text.strip()
        artist = row.find_all('td')[2].text.strip()
        yield {'year': year, 'rank': rank, 'title': title, 'artist': artist}


if __name__ == "__main__":
    for year in range(2000, 2026):
        #some years had this error: index out of range, so I will skip those years
        skip_years = [2000, 2008, 2012, 2013, 2015, 2016, 2024]

        if year in skip_years:
            continue
        file_path = f"data/raw/billboard_top_100_songs_{year}.json"
        if not Path(file_path).exists():
            with open(file_path,'w',newline="", encoding='utf-8') as f:
                        json.dump(fetch_year(year), f, ensure_ascii=False, indent=4)
            print(f"Scraped 100 songs for year {year}")
        else:
             print(f"File for year {year} already exists. Skipping scraping.")