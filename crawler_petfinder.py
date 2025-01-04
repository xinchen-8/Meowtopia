from classes import *

import requests
from bs4 import BeautifulSoup
import csv

BASE_URL_UP = "https://www.petfinder.com/search/?page="
BASE_URL_DN = "&limit[]=40&status=adoptable&token=Zn0i6XWR_gq93HFIoYujKEQxdwKSMQNVMJJp551gI98&distance[]=Anywhere&type[]=cats&sort[]=nearest&location_slug[]=gu%2Fpiti-municipality&include_transportable=true"
genderlist = ['Female', 'Male']

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6",
    "referer": "https://www.petfinder.com/search/cats-for-adoption/gu/piti-municipality/?distance=Anywhere",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "x-requested-with": "XMLHttpRequest",
}

# Cookie 設置
cookies = {
    "PFSESSION": "fa9250a1b9bbcdfefefec09fd87f27e6",
    "optimizelyEndUserId": "oeu1735714351933r0.7128938969752034",
    "user_location_slug": "gu/piti-municipality",
}


def fetch_api(url):
    url_list = []
    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        print("Information fetch successfully!")
        for i in response.json()['result']['animals']:
            url_list.append('https://www.petfinder.com/cat/jiji-'+str(i['animal']['id'])+'/gu/mangilao/guam-animals-in-need-gu01/')
            print('https://www.petfinder.com/cat/jiji-'+str(i['animal']['id'])+'/gu/mangilao/guam-animals-in-need-gu01/')
    else:
        print(f"Request failed, status code: {response.status_code}")
    return url_list

def fetch_element_api(url):
    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        name_tag = soup.find('span','u-displayBlock u-vr4x u-vr2x@minMd')
        name = name_tag.text.strip() if name_tag else "Unknown"
        #print(name)

        img_tag = soup.find('div', 'imgMask imgMask_circleXxl m-imgMask_borderWhite m-imgMask_center')
        img_url = img_tag.find('img')["src"] if img_tag else "Unknown"
        #print(img_url)

        ul_element = soup.find('ul', {'class': 'hrArray hrArray_bulletDivided u-inlineBlock'})

        if ul_element:
            pkts = {}
            try:
                key_items = ['Hair', 'Age', 'Gender', 'Size']
                items = [li.text.strip() for li in ul_element.find_all('li', {'class': 'txt'})]
                for i, j in zip(key_items, items):
                    pkts[i] = j

                key_detail = soup.find_all('dt', 'txt m-txt_lg m-txt_bold m-txt_uppercase')
                details = soup.find_all('dd', 'txt')

                for i, j in zip(key_detail, details):
                    pkts[i.text] = j.text

                # Make sure these variables are defined elsewhere in your code
                return (name, img_url, url, pkts)
            except Exception as e:
                print(f'Error processing pkt columns: {e}')
        else:
            return "Target <ul> element not found."


def make_package(cat):
    pkts = []
    
    print(cat)
    try:
        try:
            if(cat[3]['Age']=='Kitten'):
                age = -2
            elif(cat[3]['Age']=='Young'):
                age = -3
            elif(cat[3]['Age']=='Adult'):
                age = -4
            elif(cat[3]['Age']=='Adult'):
                age = 0
            else:
                age = -1
        except:
            age = -1
            
        new_cat = GlobalCat(
            name = cat[0],
            age = age,
            gender = genderlist.index(cat[3]['Gender']) if cat[3]['Gender'] in genderlist else -1,
            health_status = cat[3]['Health'] if 'Health' in cat[3] else 'Unknown',
            personality = cat[3]['Characteristics'] if 'Characteristics' in cat[3] else 'Unknown',
            img = cat[1],
            linker = cat[2],
            src = 'petfinder'
            )
    except: print('Error pckt')
    else:
        pkts.append(new_cat)
    return pkts
    
def do():
    print("Fetching cat adoption details...")
    
    for i in range(1, 11):
        url_list = fetch_api(BASE_URL_UP+str(i)+BASE_URL_DN)

        for link in url_list:

            cats = fetch_element_api(link)
            pkts = make_package(cats)

            with app.app_context():
                try:
                    db.session.add_all(pkts)
                    db.session.commit()
                    print(f"Page data committed successfully.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing page: {e}")


def climb_petfinder(delete): #main
    if delete:
        with app.app_context():
            db.session.query(GlobalCat).delete()
            db.session.commit()
    do()
climb_petfinder(True)