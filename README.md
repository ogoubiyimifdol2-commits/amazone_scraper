# Mini-projet : Web scraping en Python (POO / MVC)

Projet de la **Séance 2** (Institut Ivoirien de Technologie) : récupérer des données
sur un site, les enregistrer en CSV et afficher 3 statistiques.

## Sites pris en charge (`SITE` dans `config.py`)
- **`"amazon"` (par défaut)** : amazon.fr, 3 recherches du rayon High-Tech servant de
  « catégories » : *Smartphone*, *Ordinateur portable*, *Casque audio* (3 pages max chacune).
  Navigation avec **Selenium** (`CLIENT_AMAZON = "selenium"`) ou `requests`.
- **`"books"`** : [books.toscrape.com](https://books.toscrape.com/), site conçu pour
  s'entraîner (*Travel*, *Mystery*, *Science Fiction*), sans aucune restriction.

### Avertissement sur Amazon
Les conditions d'utilisation d'Amazon limitent l'accès automatisé et son `robots.txt`
interdit certains chemins. Ce projet est **pédagogique, à très faible volume** (≈ 9 pages,
3 s de pause entre requêtes, User-Agent identifiable) et :
- **refuse** de télécharger une URL interdite par `robots.txt` ;
- **s'arrête** si Amazon affiche un CAPTCHA, sans tenter de le contourner ;
- ne collecte aucune donnée personnelle (titre, prix, note, URL du produit).

Si Amazon bloque, repasser sur `SITE = "books"` donne un résultat garanti.
Les sélecteurs CSS Amazon sont dans `app/scraper/parsing_amazon.py` (le HTML d'Amazon change souvent).

## Respect des règles du cours
| Règle | Mise en œuvre |
|---|---|
| `robots.txt` et CGU | `ClientHTTP.est_autorise()` lit `robots.txt` avant chaque requête ; CGU documentées ci-dessus |
| Politesse | pause entre deux requêtes (`DELAI_ENTRE_REQUETES`) et `User-Agent` identifiable |
| Données personnelles | aucune |
| API d'abord | Amazon propose l'API *Product Advertising* (réservée aux affiliés) ; non utilisable ici |

## Architecture (MVC)
```
main.py                      point d'entrée
config.py                    paramètres (URL, pauses, chemins)
app/
  models/      produit.py    classe Produit (dataclass)
               depot.py      classe Depot : SQLite + statistiques
  views/       console_view.py   affichage console
               export_view.py    export CSV
  controllers/ scraping_controller.py   orchestre scraper -> modèle -> vues
  scraper/     driver.py     ClientHTTP / ClientSelenium (robots.txt, pauses)
               parsing.py    extraction BeautifulSoup (sélecteurs CSS)
               parsing_amazon.py extraction des résultats Amazon
               amazon_scraper.py scraping Amazon (arrêt si CAPTCHA)
               books_scraper.py  scraping de books.toscrape.com
data/produits_<site>.db      base SQLite
exports/produits_<site>.csv  export CSV
tests/                       tests pytest (hors-ligne, faux sites)
```

## Installation et lancement
```bash
python -m venv .venv
.venv\Scripts\activate           # macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Google Chrome doit être installé (Selenium).

## Statistiques affichées
1. **Moyenne** des prix
2. **Maximum** : prix le plus élevé (avec le titre du produit)
3. **Nombre de produits par catégorie**

## Résultats (exécution du 24/10/2026, amazon.fr)
- 471 produits scrapés : Casque audio 167, Ordinateur portable 161, Smartphone 143
- Prix moyen : 312,10 € ; prix maximum : 3 299,99 € (ASUS ProArt P16)
- Données : `exports/produits_amazon.csv` et `data/produits_amazon.db`

## Tests
```bash
python -m pytest -q
```
28 tests, sans réseau : de faux sites reproduisent la structure HTML d'Amazon et de
books.toscrape.com.

## Choix techniques
- Selenium pour Amazon (contenu dynamique), `requests` pour books.toscrape.com (statique).
- Sélecteurs CSS Amazon : `div[data-component-type="s-search-result"]`, `h2`,
  `span.a-price span.a-offscreen`, `span.a-icon-alt`, `a.s-pagination-next`.
- SQLite avec l'URL comme clé primaire : relancer le scraping ne crée pas de doublons.