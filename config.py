"""Paramètres du projet de scraping."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Site à scraper : "amazon" ou "books" (books.toscrape.com, site conçu pour s'entraîner)
SITE = "amazon"

PAGES_MAX = 3               # pages maximum scrapées par catégorie
DELAI_ENTRE_REQUETES = 3.0  # secondes de pause entre deux requêtes
TIMEOUT = 30                # secondes avant abandon d'une requête
USER_AGENT = "IIT-MiniProjetScraper/1.0 (projet scolaire, Institut Ivoirien de Technologie)"

# --- Amazon : 3 « catégories » = 3 recherches du rayon High-Tech --------------
AMAZON_URL = "https://www.amazon.fr/"
AMAZON_RECHERCHES = {
    "Smartphone": AMAZON_URL + "s?k=smartphone",
    "Ordinateur portable": AMAZON_URL + "s?k=ordinateur+portable",
    "Casque audio": AMAZON_URL + "s?k=casque+audio",
}
HEADLESS = False            # Selenium sans fenêtre (False pour voir le navigateur)
CLIENT_AMAZON = "selenium"  # "selenium" (exécute le JavaScript) ou "requests"

# --- Books to Scrape ----------------------------------------------------------
BASE_URL = "https://books.toscrape.com/"
CATEGORIES = ["Travel", "Mystery", "Science Fiction"]

DB_PATH = BASE_DIR / "data" / f"produits_{SITE}.db"
EXPORT_DIR = BASE_DIR / "exports"
CSV_PATH = EXPORT_DIR / f"produits_{SITE}.csv"
DEVISE = "€" if SITE == "amazon" else "£"