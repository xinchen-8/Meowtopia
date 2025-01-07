from classes import *

import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://www.catwelfare.org/adoptions/"
genderlist = ['Female', 'Male']

def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_cat_detail(element_soup):
    target = element_soup.find('article', 'post')
    rows = target.find('table', id='wobs-table').find_all('tr')
    data = {}
    for row in rows:
        th = row.find("th").text.strip()  
        td = row.find("td").text.strip()  
        data[th] = td
        
    rows = target.find('div', 'entry-content').find_all('p')
    data['intro'] = ''
    
    for row in rows[1:]:
        data['intro'] += row.text
    data['intro'] = data['intro'][0:300]
    print(data['intro'])
    return data


def extract_cat_element(soup):
    cats = []
    cat_cards = soup.find_all('div', class_='wpc-product')  # Adjust selector based on actual HTML structure

    for card in cat_cards:
        try:
            title_tag = card.find("p", class_="wpc-title")
            name = title_tag.text.strip() if title_tag else "No Title" #貓咪名稱
            detail_url = title_tag.find("a")["href"]
            img_tag = card.find("img")
            img_url = img_tag["src"] if img_tag else "No Image URL" #貓咪圖片

            print(name)
            print(img_url)
            print(detail_url)

            element_soup = fetch_page(detail_url)
            detail = extract_cat_detail(element_soup)

        except AttributeError:
            print("Error parsing a cat card")
        else:
            cats.append((name, img_url, detail_url, detail))
    return cats

def make_package(cats):
    pkts = []
    for c in cats:
        
        try:
            try:
                if(c[3]['Age'].split()[1]=='year(s)'):
                    age = int(c[3]['Age'].split()[0])
                elif(c[3]['Age'].split()[1]=='month(s)'):
                    age = 0
                else:
                    age = -1
            except:
                age = -1
            
            new_cat = GlobalCat(
                name = c[0],
                age = age,
                gender = genderlist.index(c[3]['Gender']) if c[3]['Gender'] in genderlist else -1,
                health_status = 'Unknown',
                personality = c[3]['intro'],
                img = c[1],
                linker = c[2],
                src = 'catwelfare'
            )
        except: print('Error pckt')
        else:
            pkts.append(new_cat)
    return pkts
            
def do(url):
    print("Fetching cat adoption details...")
    for page_index in range(1, 11):

        soup = fetch_page(url+str(page_index))
        if not soup:
            print("Failed to fetch the main page.")
            return
        cats = extract_cat_element(soup)
        pkts = make_package(cats)

        print(pkts)
        with app.app_context():
            db.session.add_all(pkts)
            db.session.commit()
            
    
def crawl_catwelfare(delete):
    if delete:
        with app.app_context():
            db.session.query(GlobalCat).delete()
            db.session.commit()
    do(BASE_URL)

#crawler_catwelfare(True)