import csv

import pytest

from app.controllers.scraping_controller import ScrapingController
from app.models.depot import Depot
from app.scraper.books_scraper import BooksScraper
from app.scraper.driver import ErreurScraping
from app.views.console_view import ConsoleView
from app.views.export_view import ExportView
from tests.fixtures import BASE, FauxClient


def _controleur(tmp_path, categories, pages_max=3):
    client = FauxClient()
    scraper = BooksScraper(client, BASE, pages_max)
    return ScrapingController(scraper, Depot(":memory:"), ConsoleView(), ExportView(),
                              categories, tmp_path / "out.csv"), client


def test_flux_complet(tmp_path, capsys):
    ctrl, client = _controleur(tmp_path, ["Travel", "Mystery", "Science Fiction"])
    stats = ctrl.executer()

    assert stats["total"] == 7
    assert stats["prix_moyen"] == pytest.approx((10 + 38.95 + 47.82 + 20 + 12 + 30.5 + 22) / 7)
    assert stats["plus_cher"].titre == "Sharp Objects"
    assert stats["par_categorie"] == {"Science Fiction": 3, "Mystery": 2, "Travel": 2}
    assert len(client.urls_demandees) >= 4          # consigne : au moins 3 pages
    sortie = capsys.readouterr().out
    assert "Prix moyen" in sortie and "Prix maximum" in sortie and "Nombre par catégorie" in sortie

    with open(tmp_path / "out.csv", encoding="utf-8-sig") as f:
        lignes = list(csv.DictReader(f))
    assert len(lignes) == 7


def test_pages_max_limite_la_pagination(tmp_path):
    ctrl, client = _controleur(tmp_path, ["Mystery"], pages_max=1)
    ctrl.executer()
    assert not any("page-2" in u for u in client.urls_demandees)


def test_categorie_inconnue(tmp_path, capsys):
    ctrl, _ = _controleur(tmp_path, ["Cuisine"])
    assert ctrl.executer() is None
    assert "Catégorie inconnue" in capsys.readouterr().out
    with pytest.raises(ErreurScraping):
        ctrl.scraper.scraper(["Cuisine"])