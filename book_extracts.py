
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import re

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:160.0) Gecko/20100101 Firefox/160.0',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

tous_les_produits = []

for numero_page in range(1, 51):
    url = f'https://books.toscrape.com/catalogue/page-{numero_page}.html'
    print(f"On scrape la page {numero_page}/50...")

    response = requests.get(url, headers=header, timeout=30)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='product_pod')

    if len(articles) == 0:
        print("Plus d'articles, on s'arrête")
        break

    for article in articles:
        nom = article.find('h3').find('a')['title']
        prix_texte = article.find('p', class_='price_color').get_text(strip=True)
        prix_nombre = float(re.sub(r'[^0-9.]', '', prix_texte))
        note = article.find('p', class_='star-rating')['class'][1]
        dispo = article.find('p', class_='instock availability').get_text(strip=True)

        tous_les_produits.append({
            'Nom': nom,
            'Prix': prix_nombre,
            'Note': note,
            'Dispo': dispo,
            'Page': numero_page,
        })

    time.sleep(0.5)

df = pd.DataFrame(tous_les_produits)
print(f"TOTAL : {len(df)} livres extraits")
print(df.head())
df.to_csv('tous_les_livres.csv', index=False, encoding='utf-8')
print("Sauvegardé !")
