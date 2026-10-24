"""Orchestration du scraping : navigation catégorie par catégorie, page par page."""
from app.models.produit import Produit
from app.scraper import parsing
from app.scraper.driver import ClientHTTP, ErreurScraping


class BooksScraper:
    def __init__(self, client: ClientHTTP, url_accueil: str, pages_max: int):
        self.client = client
        self.url_accueil = url_accueil
        self.pages_max = pages_max
        self.pages_visitees = 0

    def categories_disponibles(self) -> dict[str, str]:
        html = self.client.get(self.url_accueil)
        self.pages_visitees += 1
        return parsing.parser_categories(html, self.url_accueil)

    def scraper_categorie(self, nom: str, url: str) -> list[Produit]:
        produits: list[Produit] = []
        prochaine: str | None = url
        for _ in range(self.pages_max):
            if prochaine is None:
                break
            html = self.client.get(prochaine)
            self.pages_visitees += 1
            produits.extend(parsing.parser_produits(html, prochaine, nom))
            prochaine = parsing.page_suivante(html, prochaine)
        return produits

    def scraper(self, noms_categories: list[str]) -> list[Produit]:
        disponibles = self.categories_disponibles()
        tous: list[Produit] = []
        for nom in noms_categories:
            if nom not in disponibles:
                raise ErreurScraping(
                    f"Catégorie inconnue : {nom!r}. Disponibles : {', '.join(disponibles)}"
                )
            tous.extend(self.scraper_categorie(nom, disponibles[nom]))
        return tous