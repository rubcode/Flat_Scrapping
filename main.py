from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import pandas as pd
import json
from bs4 import BeautifulSoup
import time
from chat import *


path = "Outputs/flats.csv"
sentFlats = pd.read_csv(path,header='infer',delimiter=",")
print(len(sentFlats))

browser = uc.Chrome()
suburn = "portales"
url = f"https://propiedades.com/{suburn}/departamentos-renta"
browser.get(url)
browser.implicitly_wait(10)
html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')
countItems = int(soup.find_all(class_='crfbvO')[0].text.split("de")[1].split(" ")[1])
page = 1
flatsData = []

print(f"El sitio web tiene {countItems} páginas")
print("******************")
while (page <= countItems):
    print(f"Scrapping Página {page}")
    print("******************")
    urlPage = f"https://propiedades.com/{suburn}/departamentos-renta?pagina={page}"
    browser.get(urlPage)
    browser.implicitly_wait(10)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    flats = soup.find_all(class_='kbLgkU')
    print(f"Hay {len(flats)} departamentos en esta pagina")
    print("******************")
    for flat in flats:
        link = flat.find('a')
        if link:
            url = link.get("href")
        content = flat.text.replace("USD","MXN")
        price = content.split("DepartamentoRenta")
        content = price[1]
        price = price[1].split(" MXN")
        price = price[0]
        price = int(price.replace(",","").replace("$",""))
        if(price <= 17500):
            content = content.split("ContactarWhatsApp")
            content = content[0]
            content = content.split("ID: ")
            id = content[1]
            content = content[0].split("Ver propiedad")[1]
            content = content.split("m2")
            address = ''
            if(len(content) > 1):
                address = content[1]
            
            content = content[0]
            roomsFlat = content.split(" ")
            flatsData.append({"id": id,
                            "rooms": roomsFlat[0],
                            "bathrooms": roomsFlat[1], 
                            "m2":roomsFlat[2],
                            "price": price,
                            "address": address,
                            "url": url})
    page = page + 1
    time.sleep(1)

data = pd.DataFrame(flatsData)
data['is_sent'] = data['id'].apply(lambda x: 0 if not sentFlats['id'].isin([x]).any() else 1)
data = data[data['is_sent'] == 1]

for index,row in data.iterrows():
    message = str(row.url)
    sendChat(url)
sentFlats = pd.concat([sentFlats, data], ignore_index=True)
sentFlats.to_csv("Outputs/flats.csv",header=True,index=False)