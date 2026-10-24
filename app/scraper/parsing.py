"""Fonctions d'extraction (BeautifulSoup + sélecteurs CSS). Aucune requête réseau ici."""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.models.produit import Produit

NOTES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def convertir_prix(texte: str) -> float:
    """'£51.77' -> 51.77 ; '1 299,00 €' -> 1299.0 ; '1.299,99 €' -> 1299.99."""
    brut = re.sub(r"[\s\u00a0\u202f]", "", texte or "")
    trouve = re.search(r"\d[\d.,]*", brut)
    if not trouve:
        raise ValueError(f"Prix illisible : {texte!r}")
    nombre = trouve.group().rstrip(".,")
    if "," in nombre and "." in nombre:           # le dernier séparateur est la décimale
        decimal = "," if nombre.rfind(",") > nombre.rfind(".") else "."
        milliers = "." if decimal == "," else ","
        nombre = nombre.replace(milliers, "").replace(decimal, ".")
    elif "," in nombre:
        if re.fullmatch(r"\d{1,3}(,\d{3})+", nombre):  # 1,299 -> milliers
            nombre = nombre.replace(",", "")
        else:                                            # 12,50 -> décimale
            nombre = nombre.replace(",", ".")
    elif nombre.count(".") > 1:                   # 1.299.000 -> milliers
        nombre = nombre.replace(".", "")
    return float(nombre)


def extraire_note(classes: list[str]) -> int:
    """['star-rating', 'Three'] -> 3 (0 si inconnue)."""
    for nom in classes:
        if nom in NOTES:
            return NOTES[nom]
    return 0


def parser_categories(html: str, url_page: str) -> dict[str, str]:
    """Menu latéral : {nom de catégorie: URL absolue}."""
    soupe = BeautifulSoup(html, "html.parser")
    liens = soupe.select("div.side_categories ul li ul li a")
    return {a.get_text(strip=True): urljoin(url_page, a["href"]) for a in liens}


def parser_produits(html: str, url_page: str, categorie: str) -> list[Produit]:
    soupe = BeautifulSoup(html, "html.parser")
    produits = []
    for fiche in soupe.select("article.product_pod"):
        lien = fiche.select_one("h3 a")
        prix = fiche.select_one("p.price_color")
        stock = fiche.select_one("p.availability")
        note = fiche.select_one("p.star-rating")
        if not (lien and prix):
            continue  # fiche incomplète : on l'ignore plutôt que de planter
        produits.append(
            Produit(
                titre=lien["title"],
                prix=convertir_prix(prix.get_text()),
                en_stock="in stock" in (stock.get_text().lower() if stock else ""),
                note=extraire_note(note.get("class", [])) if note else 0,
                categorie=categorie,
                url=urljoin(url_page, lien["href"]),
            )
        )
    return produits


def page_suivante(html: str, url_page: str) -> str | None:
    lien = BeautifulSoup(html, "html.parser").select_one("li.next a")
    return urljoin(url_page, lien["href"]) if lien else None