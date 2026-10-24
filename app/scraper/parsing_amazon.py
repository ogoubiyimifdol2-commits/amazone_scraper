"""Extraction des résultats de recherche Amazon (aucune requête réseau ici).

Les sélecteurs reflètent la page de résultats amazon.fr ; Amazon change souvent son
HTML : en cas de 0 produit, inspecter la page (F12) et adapter les constantes ci-dessous.
"""
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.models.produit import Produit
from app.scraper.parsing import convertir_prix

SEL_RESULTAT = 'div[data-component-type="s-search-result"]'
SEL_TITRE = "h2"
SEL_PRIX = "span.a-price span.a-offscreen"
SEL_NOTE = "span.a-icon-alt"
SEL_SUIVANT = "a.s-pagination-next"

MARQUES_CAPTCHA = (
    "api-services-support@amazon", "/errors/validatecaptcha",
    "saisissez les caractères", "enter the characters you see", "robot check",
)


def est_captcha(html: str) -> bool:
    bas = html.lower()
    return any(marque in bas for marque in MARQUES_CAPTCHA)


def extraire_note_amazon(texte: str) -> float:
    """'4,5 sur 5 étoiles' -> 4.5 (0.0 si absent)."""
    trouve = re.search(r"\d(?:[.,]\d)?", texte or "")
    return float(trouve.group().replace(",", ".")) if trouve else 0.0


def parser_resultats(html: str, url_page: str, categorie: str) -> list[Produit]:
    soupe = BeautifulSoup(html, "html.parser")
    produits = []
    for carte in soupe.select(SEL_RESULTAT):
        asin = carte.get("data-asin", "").strip()
        titre_el = carte.select_one(SEL_TITRE)
        prix_el = carte.select_one(SEL_PRIX)
        if not (asin and titre_el and prix_el):
            continue  # publicité, carte sans prix ou sans identifiant : ignorée
        titre = titre_el.get_text(" ", strip=True) or titre_el.get("aria-label", "")
        note_el = carte.select_one(SEL_NOTE)
        produits.append(
            Produit(
                titre=titre,
                prix=convertir_prix(prix_el.get_text()),
                en_stock=True,  # un prix affiché = article proposé à la vente
                note=extraire_note_amazon(note_el.get_text()) if note_el else 0.0,
                categorie=categorie,
                url=urljoin(url_page, f"/dp/{asin}"),  # URL canonique, sans pistage
            )
        )
    return produits


def page_suivante_amazon(html: str, url_page: str) -> str | None:
    lien = BeautifulSoup(html, "html.parser").select_one(SEL_SUIVANT)
    return urljoin(url_page, lien["href"]) if lien and lien.get("href") else None