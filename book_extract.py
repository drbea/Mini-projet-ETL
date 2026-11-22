import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import re

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:160.0) Gecko/20100101 Firefox/160.0',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
}


def find_articles(url, tag_name='article', class_name='product_pod', parser='html.parser', timeout=30):
    """EXTRACT : télécharge une page et renvoie la liste des articles (vide si aucun)."""
    response = requests.get(url, headers=header, timeout=timeout)
    response.encoding = 'utf-8'  # <-- CORRECTION 1 : sinon '£' devient 'Â£'
    soup = BeautifulSoup(response.text, parser)
    return soup.find_all(tag_name, class_=class_name)


def extraire_livre(article, numero_page):
    """TRANSFORM : transforme un <article> HTML en dictionnaire propre."""
    prix_texte = article.find('p', class_='price_color').get_text(strip=True)
    return {
        'Nom': article.find('h3').find('a')['title'],
        'Prix': float(re.sub(r'[^0-9.]', '', prix_texte)),  # <-- CORRECTION 2
        'Note': article.find('p', class_='star-rating')['class'][1],
        'Dispo': article.find('p', class_='instock availability').get_text(strip=True),
        'Page': numero_page,
    }


def display_books(df):
    """Affiche le nombre de livres et les premières lignes."""
    if df.empty:
        print("Aucun livre à afficher")
        return
    print(f"TOTAL : {len(df)} livres extraits")
    print(df.head())


def save_all_books(df, filename='tous_les_livres.csv', encoding='utf-8'):
    """LOAD : enregistre le DataFrame dans un fichier CSV."""
    df.to_csv(filename, index=False, encoding=encoding)
    print(f"Sauvegardé dans {filename} !")


def main():
    TOTAL_PAGES = 50
    tous_les_produits = []

    for numero_page in range(1, TOTAL_PAGES + 1):
        print(f"On scrape la page {numero_page}/{TOTAL_PAGES}...")
        url = f'https://books.toscrape.com/catalogue/page-{numero_page}.html'
        articles = find_articles(url)

        if not articles:
            print("Plus d'articles, on s'arrête")
            break


        for article in articles:
            livre = extraire_livre(article, numero_page)
            tous_les_produits.append(livre)
            print(f"\n {livre}")
            
        time.sleep(0.5)

    df = pd.DataFrame(tous_les_produits)
    display_books(df)
    save_all_books(df)


if __name__ == "__main__":
    main()
