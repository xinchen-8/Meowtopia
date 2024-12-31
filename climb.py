from classes import *

import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.catwelfare.org/adoptions/"

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_cat_detail(element_soup):
    rows = element_soup.find('table', id='wobs-table').find_all("tr")
    data = {}
    for row in rows:
        th = row.find("th").text.strip()  
        td = row.find("td").text.strip()  
        data[th] = td
    return data


def extract_cat_element(soup):
    cats = []
    cat_cards = soup.find_all('div', class_='wpc-product')  # Adjust selector based on actual HTML structure

    for card in cat_cards:
        try:
            title_tag = card.find("p", class_="wpc-title")
            name = title_tag.text.strip() if title_tag else "No Title" #貓咪名稱
            detail_url = title_tag.find("a")["href"]
            print(name)
            print(detail_url)

            img_tag = card.find("img")
            img_url = img_tag["src"] if img_tag else "No Image URL" #貓咪圖片
            print(img_url)

            element_soup = fetch_page(detail_url)
            detail = extract_cat_detail(element_soup)

        except AttributeError:
            print("Error parsing a cat card")
        else:
            cats.append((name, img_url, detail))
    return cats

def make_package(cats):
    pkts = []
    for c in cats:
        try:
            new_cat = GlobalCat(
                name = c[0],
                age = c[2]['Age'],
                gender = c[2]['Gender'],
                health_status = 'Unknown',
                personality = 'Unknown',
                img = c[1]
                #adoption_status = 'not yet'
            )
        except: print('Error pckt')
        else:
            pkts.append(new_cat)
    return pkts
            


def main(url):
    pkts = []
    print("Fetching cat adoption details...")
    for page_index in range(1, 5):

        soup = fetch_page(url+str(page_index))
        if not soup:
            print("Failed to fetch the main page.")
            return

        cats = extract_cat_element(soup)
        pkts += make_package(cats)
    return pkts

if __name__ == "__main__":
    with app.app_context():
        db.session.query(GlobalCat).delete()
        db.session.commit()
        db.session.add_all(main(BASE_URL))
        db.session.commit()
