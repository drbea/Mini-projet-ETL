import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:160.0) Gecko/20100101 Firefox/160.0',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}

# EXTRACT : une seule page, pas de boucle sur les pages
url = 'https://books.toscrape.com/catalogue/page-1.html'
response = requests.get(url, headers=header, timeout=30)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
articles = soup.find_all('article', class_='product_pod')
print(f"{len(articles)} livres trouvés sur la page 1")

# TRANSFORM : on parcourt les articles de CETTE page
produits = []
for article in articles:
    nom = article.find('h3').find('a')['title']
    prix_texte = article.find('p', class_='price_color').get_text(strip=True)
    prix_nombre = float(re.sub(r'[^0-9.]', '', prix_texte))
    note = article.find('p', class_='star-rating')['class'][1]
    dispo = article.find('p', class_='instock availability').get_text(strip=True)

    produits.append({
        'Nom': nom,
        'Prix': prix_nombre,
        'Note': note,
        'Dispo': dispo,
    })

# LOAD
df = pd.DataFrame(produits)
print(df.head())
df.to_csv('livres_page1.csv', index=False, encoding='utf-8')
print("Sauvegardé !")
