import pytest

from app.scraper import parsing
from tests.fixtures import ACCUEIL, BASE, PAGES


@pytest.mark.parametrize("texte, attendu", [
    ("£51.77", 51.77),
    ("Â£51.77", 51.77),
    ("  12,50 € ", 12.5),
    ("10", 10.0),
])
def test_convertir_prix(texte, attendu):
    assert parsing.convertir_prix(texte) == attendu


def test_convertir_prix_invalide():
    with pytest.raises(ValueError):
        parsing.convertir_prix("gratuit")


def test_extraire_note():
    assert parsing.extraire_note(["star-rating", "Three"]) == 3
    assert parsing.extraire_note(["star-rating"]) == 0


def test_parser_categories():
    cats = parsing.parser_categories(ACCUEIL, BASE)
    assert set(cats) == {"Travel", "Mystery", "Science Fiction"}
    assert cats["Travel"] == BASE + "catalogue/category/books/travel_2/index.html"


def test_parser_produits():
    url = BASE + "catalogue/category/books/travel_2/index.html"
    produits = parsing.parser_produits(PAGES[url], url, "Travel")
    assert len(produits) == 2
    p = produits[0]
    assert (p.titre, p.prix, p.note, p.en_stock, p.categorie) == (
        "It Happened in Italy", 10.0, 2, True, "Travel")
    assert p.url == BASE + "catalogue/it-happened_1/index.html"


def test_stock_epuise():
    url = BASE + "catalogue/category/books/mystery_3/page-2.html"
    assert parsing.parser_produits(PAGES[url], url, "Mystery")[0].en_stock is False


def test_page_suivante():
    url = BASE + "catalogue/category/books/mystery_3/index.html"
    assert parsing.page_suivante(PAGES[url], url) == BASE + "catalogue/category/books/mystery_3/page-2.html"
    assert parsing.page_suivante(PAGES[BASE + "catalogue/category/books/travel_2/index.html"], url) is None