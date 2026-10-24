"""Scraping d'Amazon : une recherche par « catégorie », pagination limitée.

S'arrête dès qu'Amazon affiche un CAPTCHA : on ne le contourne pas.
"""
from app.models.produit import Produit
from app.scraper import parsing_amazon as pa
from app.scraper.driver import ErreurScraping


class AmazonScraper:
    def __init__(self, client, recherches: dict[str, str], pages_max: int):
        self.client = client
        self.recherches = recherches
        self.pages_max = pages_max
        self.pages_visitees = 0

    def _telecharger(self, url: str) -> str:
        html = self.client.get(url)
        self.pages_visitees += 1
        if pa.est_captcha(html):
            raise ErreurScraping(
                "Amazon a affiché un CAPTCHA (détection de robot). Arrêt volontaire : "
                "le contournement est interdit. Réessaie plus tard ou utilise SITE = \"books\"."
            )
        return html

    def scraper_categorie(self, nom: str, url: str) -> list[Produit]:
        produits: list[Produit] = []
        prochaine: str | None = url
        for _ in range(self.pages_max):
            if prochaine is None:
                break
            html = self._telecharger(prochaine)
            produits.extend(pa.parser_resultats(html, prochaine, nom))
            prochaine = pa.page_suivante_amazon(html, prochaine)
        return produits

    def scraper(self, noms_categories: list[str]) -> list[Produit]:
        tous: list[Produit] = []
        for nom in noms_categories:
            if nom not in self.recherches:
                raise ErreurScraping(
                    f"Catégorie inconnue : {nom!r}. Disponibles : {', '.join(self.recherches)}")
            tous.extend(self.scraper_categorie(nom, self.recherches[nom]))
        if not tous:
            raise ErreurScraping(
                "0 produit extrait : les sélecteurs CSS ne correspondent plus à la page. "
                "Inspecte la page (F12) et adapte app/scraper/parsing_amazon.py.")
        return tous