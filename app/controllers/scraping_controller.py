"""Contrôleur : relie le scraper, le dépôt (modèle) et les vues."""
import config
from app.models.depot import Depot
from app.scraper.amazon_scraper import AmazonScraper
from app.scraper.books_scraper import BooksScraper
from app.scraper.driver import ClientHTTP, ClientSelenium, ErreurScraping
from app.scraper.parsing_amazon import SEL_RESULTAT
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView


class ScrapingController:
    def __init__(self, scraper: BooksScraper, depot: Depot,
                 console: ConsoleView, export: ExportView, categories: list[str],
                 chemin_csv=config.CSV_PATH):
        self.scraper = scraper
        self.depot = depot
        self.console = console
        self.export = export
        self.categories = categories
        self.chemin_csv = chemin_csv

    @classmethod
    def par_defaut(cls) -> "ScrapingController":
        if config.SITE == "amazon":
            if config.CLIENT_AMAZON == "selenium":
                client = ClientSelenium(
                    config.USER_AGENT, config.DELAI_ENTRE_REQUETES, config.TIMEOUT,
                    headless=config.HEADLESS, selecteur_attente=SEL_RESULTAT)
            else:
                client = ClientHTTP(config.USER_AGENT, config.DELAI_ENTRE_REQUETES, config.TIMEOUT)
            scraper = AmazonScraper(client, config.AMAZON_RECHERCHES, config.PAGES_MAX)
            categories = list(config.AMAZON_RECHERCHES)
        else:
            client = ClientHTTP(config.USER_AGENT, config.DELAI_ENTRE_REQUETES, config.TIMEOUT)
            scraper = BooksScraper(client, config.BASE_URL, config.PAGES_MAX)
            categories = config.CATEGORIES
        return cls(scraper, Depot(config.DB_PATH), ConsoleView(config.DEVISE), ExportView(),
                   categories, config.CSV_PATH)

    def fermer(self) -> None:
        self.depot.fermer()
        fermer_client = getattr(self.scraper.client, "fermer", None)
        if fermer_client:
            fermer_client()

    def executer(self) -> dict | None:
        self.console.message(f"Scraping de {', '.join(self.categories)} "
                             f"(pause de {self.scraper.client.delai}s entre requêtes)...")
        try:
            produits = self.scraper.scraper(self.categories)
        except ErreurScraping as erreur:
            self.console.message(f"Erreur : {erreur}")
            return None

        self.depot.vider()  # on repart d'un état propre à chaque exécution
        self.depot.ajouter_tous(produits)
        stocke = self.depot.tous()

        self.console.message(f"{self.scraper.pages_visitees} pages visitées, "
                             f"{len(stocke)} produits enregistrés.")
        self.console.afficher_produits(stocke)
        chemin = self.export.exporter_csv(stocke, self.chemin_csv)
        self.console.message(f"\nCSV exporté : {chemin}")

        stats = self.depot.statistiques()
        self.console.afficher_statistiques(stats)
        return stats