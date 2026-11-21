# 📚 Mini-projet ETL : Scraping de Books to Scrape

Pipeline **ETL** (Extract – Transform – Load) en Python qui récupère le catalogue du site d'entraînement [Books to Scrape](https://books.toscrape.com) et l'enregistre dans un fichier CSV propre, prêt pour l'analyse.

## 🎯 Objectif

Construire un premier pipeline de données complet :

1. **Extract** : récupérer les pages HTML du catalogue.
2. **Transform** : nettoyer et structurer les données (prix en nombre, encodage correct...).
3. **Load** : sauvegarder le résultat dans un fichier CSV.

## 🗺️ Plan du cours

| Étape | Contenu |
|-------|---------|
| **0. Préparation** | Vérifier que Python est installé, créer l'environnement virtuel, installer les bibliothèques |
| **Partie 1** | Extraction simple : une seule page |
| **Partie 2** | Extraction complète : les 50 pages |

---

## ⚙️ Étape 0 : Préparation de l'environnement

### 0.1 Vérifier que Python est installé

Ouvre un terminal (PowerShell ou CMD sous Windows, Terminal sous macOS) et tape :

**Windows**

```bash
python --version
```

**macOS / Linux**

```bash
python3 --version
```

Résultat attendu : un numéro de version, par exemple `Python 3.12.4`. Il faut **Python 3.9 ou plus**.

Si la commande n'est pas reconnue, installe Python depuis [python.org/downloads](https://www.python.org/downloads/). Sous Windows, **coche la case « Add Python to PATH »** pendant l'installation.

Vérifie aussi `pip` :

```bash
pip --version
```

### 0.2 Créer le dossier du projet

```bash
mkdir mini-projet-etl
cd mini-projet-etl
```

### 0.3 Créer l'environnement virtuel

L'environnement virtuel isole les bibliothèques du projet, pour ne pas mélanger les versions avec d'autres projets.

**Windows**

```bash
python -m venv venv
```

**macOS / Linux**

```bash
python3 -m venv venv
```

Un dossier `venv/` est créé dans le projet.

### 0.4 Activer l'environnement virtuel

**Windows (CMD)**

```bash
venv\Scripts\activate
```

**Windows (PowerShell)**

```bash
venv\Scripts\Activate.ps1
```

Si PowerShell bloque le script, lance une fois :

```bash
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**macOS / Linux**

```bash
source venv/bin/activate
```

Quand c'est activé, `(venv)` apparaît au début de la ligne du terminal. Pour quitter l'environnement : `deactivate`.

### 0.5 Installer les bibliothèques

```bash
pip install pandas beautifulsoup4 requests
```

Sauvegarde les versions utilisées pour pouvoir refaire le projet à l'identique :

```bash
pip freeze > requirements.txt
```

Plus tard, n'importe qui pourra reconstruire l'environnement avec :

```bash
pip install -r requirements.txt
```

### 0.6 Vérifier l'installation

```bash
python -c "import pandas, bs4, requests; print('Tout est installé ✅')"
```

---

## 🔹 Partie 1 : Extraction simple (une seule page, sans boucle sur les pages)

**But** : comprendre chaque étape sur une seule page avant d'automatiser. On extrait les 20 livres de la page 1.

Fichier : `book_extract_simple.py`

```python
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
```

**Résultat attendu** : `livres_page1.csv` avec **20 lignes**.

> 💡 Dans cette partie, il n'y a pas de boucle sur les **pages**. La boucle sur les articles reste nécessaire, car une page contient 20 livres.

### Ce qu'on apprend

- Envoyer une requête HTTP avec `requests`
- Lire le HTML avec `BeautifulSoup` (`find`, `find_all`)
- Nettoyer un prix avec une regex
- Construire un `DataFrame` et l'exporter en CSV

---

## 🔹 Partie 2 : Extraction complète (avec boucle `for` sur toutes les pages)

**But** : automatiser l'extraction sur les **50 pages** du catalogue.

Fichier : `book_extract.py`

```python
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
```

**Résultat attendu** : `tous_les_livres.csv` avec **1000 lignes** (20 livres × 50 pages).

### Ce qu'on ajoute par rapport à la partie 1

| Ajout | Rôle |
|-------|------|
| `for numero_page in range(1, 51)` | Parcourt les 50 pages |
| `f'...page-{numero_page}.html'` | Construit l'URL de chaque page dynamiquement |
| `if len(articles) == 0: break` | Condition d'arrêt si une page est vide |
| `time.sleep(0.5)` | Pause entre les requêtes pour ne pas surcharger le site |
| Colonne `Page` | Garde l'origine de chaque livre |

---

## 📦 Données extraites

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `Nom` | Titre complet du livre (attribut `title`) | `A Light in the Attic` |
| `Prix` | Prix en nombre décimal (£) | `51.77` |
| `Note` | Note en lettres (One à Five) | `Three` |
| `Dispo` | Disponibilité en stock | `In stock` |
| `Page` | Numéro de la page d'origine (partie 2 seulement) | `1` |

## 🔧 Détails techniques importants

### Correction 1 : l'encodage

```python
response.encoding = 'utf-8'
```

Sans cette ligne, `requests` devine mal l'encodage et le symbole `£` s'affiche en `Â£`. On force donc l'UTF-8.

### Correction 2 : le nettoyage du prix

```python
prix_nombre = float(re.sub(r'[^0-9.]', '', prix_texte))
```

Le prix arrive sous forme de texte (`£51.77`). La regex supprime tout sauf les chiffres et le point, ce qui permet de le convertir en `float` pour faire des calculs.

### Bonnes pratiques utilisées

- **`User-Agent` + `Accept-Language`** : le script se présente comme un navigateur.
- **`timeout=30`** : évite de rester bloqué si le serveur ne répond pas.
- **`time.sleep(0.5)`** : scraping poli, sans surcharger le serveur.
- **Environnement virtuel** : dépendances isolées et reproductibles.

## 🚀 Pistes d'amélioration

- [ ] Gérer les erreurs réseau avec `try/except` et `response.raise_for_status()`.
- [ ] Convertir la colonne `Note` en nombre (`One` → 1, `Two` → 2...).
- [ ] Nettoyer la colonne `Dispo`.
- [ ] Séparer le code en trois fonctions : `extract()`, `transform()`, `load()`.
- [ ] Ajouter un système de logs au lieu des `print`.
- [ ] Charger les données dans une base SQLite ou PostgreSQL plutôt que dans un CSV.

## 📁 Structure du projet

```
mini-projet-etl/
├── venv/                      # Environnement virtuel (ne pas versionner)
├── requirements.txt           # Dépendances du projet
├── book_extract_simple.py     # Partie 1 : une seule page
├── book_extract.py            # Partie 2 : toutes les pages (boucle for)
├── livres_page1.csv           # Résultat de la partie 1
├── tous_les_livres.csv        # Résultat de la partie 2
└── README.md                  # Ce fichier
```

## ⚠️ Note

Books to Scrape est un site conçu pour s'entraîner au scraping. Pour un vrai site, vérifie toujours son `robots.txt` et ses conditions d'utilisation avant de scraper.

---

*Projet réalisé dans le cadre de ma formation en ligne en data, premier pipeline ETL.*
