import pytest

from app.models.depot import Depot
from app.models.produit import Produit


@pytest.fixture
def depot():
    d = Depot(":memory:")
    d.ajouter_tous([
        Produit("A", 10.0, True, 3, "Travel", "u1"),
        Produit("B", 30.0, True, 4, "Travel", "u2"),
        Produit("C", 50.0, False, 5, "Mystery", "u3"),
    ])
    yield d
    d.fermer()


def test_statistiques(depot):
    assert depot.prix_moyen() == pytest.approx(30.0)
    assert depot.produit_le_plus_cher().titre == "C"
    assert depot.nombre_par_categorie() == {"Travel": 2, "Mystery": 1}


def test_pas_de_doublon(depot):
    depot.ajouter(Produit("A bis", 11.0, True, 3, "Travel", "u1"))
    assert len(depot.tous()) == 3


def test_depot_vide():
    d = Depot(":memory:")
    assert d.prix_moyen() == 0.0
    assert d.produit_le_plus_cher() is None
    assert d.nombre_par_categorie() == {}