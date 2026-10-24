import pytest

from app.controllers.scraping_controller import ScrapingController
from app.models.depot import Depot
from app.scraper import parsing_amazon as pa
from app.scraper.amazon_scraper import AmazonScraper
from app.scraper.driver import ErreurScraping
from app.scraper.parsing import convertir_prix
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView

URL = "https://www.amazon.fr/s?k=smartphone"


def carte(asin, titre, prix, note="4,5 sur 5 étoiles"):
    prix_html = f'<span class="a-price"><span class="a-offscreen">{prix}</span></span>' if prix else ""
    note_html = f'<i><span class="a-icon-alt">{note}</span></i>' if note else ""
    return (f'<div data-component-type="s-search-result" data-asin="{asin}">'
            f'<h2><a href="/Truc/dp/{asin}/ref=sr_1_1?crid=XYZ"><span>{titre}</span></a></h2>'
            f'{note_html}{prix_html}</div>')


def page(cartes, suivante=None):
    nav = f'<a class="s-pagination-next" href="{suivante}">Suivant</a>' if suivante else \
          '<span class="s-pagination-next s-pagination-disabled">Suivant</span>'
    return f"<html><body>{''.join(cartes)}{nav}</body></html>"


PAGE_1 = page([
    carte("B0AAA", "Phone Alpha 128 Go", "299,99 €"),
    carte("B0BBB", "Phone Beta Pro", "1 099,00 €", note="4,0 sur 5 étoiles"),
    carte("B0CCC", "Sans prix (indisponible)", None),
    carte("", "Publicité sans ASIN", "10,00 €"),
], suivante="/s?k=smartphone&page=2")
PAGE_2 = page([carte("B0DDD", "Phone Gamma", "149,50 €", note=None)])
CAPTCHA = "<html><body>Saisissez les caractères que vous voyez ci-dessous</body></html>"


class FauxClient:
    delai = 0

    def __init__(self, pages):
        self.pages = pages
        self.demandees = []

    def get(self, url):
        self.demandees.append(url)
        return self.pages[url]


@pytest.mark.parametrize("texte, attendu", [
    ("299,99 €", 299.99),
    ("1 099,00 €", 1099.0),
    ("1\u202f099,00\u00a0€", 1099.0),
    ("1.299,99 €", 1299.99),
    ("1,299.99", 1299.99),
    ("£51.77", 51.77),
])
def test_convertir_prix_formats(texte, attendu):
    assert convertir_prix(texte) == attendu


def test_note_amazon():
    assert pa.extraire_note_amazon("4,5 sur 5 étoiles") == 4.5
    assert pa.extraire_note_amazon("") == 0.0


def test_parser_resultats():
    produits = pa.parser_resultats(PAGE_1, URL, "Smartphone")
    assert [p.titre for p in produits] == ["Phone Alpha 128 Go", "Phone Beta Pro"]
    assert produits[1].prix == 1099.0 and produits[1].note == 4.0
    assert produits[0].url == "https://www.amazon.fr/dp/B0AAA"


def test_pagination_et_captcha():
    assert pa.page_suivante_amazon(PAGE_1, URL) == "https://www.amazon.fr/s?k=smartphone&page=2"
    assert pa.page_suivante_amazon(PAGE_2, URL) is None
    assert pa.est_captcha(CAPTCHA) and not pa.est_captcha(PAGE_1)


def test_scraping_amazon_complet(tmp_path):
    client = FauxClient({URL: PAGE_1, "https://www.amazon.fr/s?k=smartphone&page=2": PAGE_2})
    scraper = AmazonScraper(client, {"Smartphone": URL}, pages_max=3)
    ctrl = ScrapingController(scraper, Depot(":memory:"), ConsoleView("€"), ExportView(),
                              ["Smartphone"], tmp_path / "a.csv")
    stats = ctrl.executer()
    assert stats["total"] == 3
    assert stats["plus_cher"].titre == "Phone Beta Pro"
    assert stats["prix_moyen"] == pytest.approx((299.99 + 1099 + 149.5) / 3)
    assert stats["par_categorie"] == {"Smartphone": 3}


def test_captcha_arrete_le_scraping(tmp_path, capsys):
    scraper = AmazonScraper(FauxClient({URL: CAPTCHA}), {"Smartphone": URL}, pages_max=3)
    ctrl = ScrapingController(scraper, Depot(":memory:"), ConsoleView("€"), ExportView(),
                              ["Smartphone"], tmp_path / "a.csv")
    assert ctrl.executer() is None
    assert "CAPTCHA" in capsys.readouterr().out
    assert not (tmp_path / "a.csv").exists()


def test_zero_produit_signale_les_selecteurs_obsoletes():
    scraper = AmazonScraper(FauxClient({URL: "<html><body>rien</body></html>"}),
                            {"Smartphone": URL}, pages_max=1)
    with pytest.raises(ErreurScraping, match="sélecteurs"):
        scraper.scraper(["Smartphone"])