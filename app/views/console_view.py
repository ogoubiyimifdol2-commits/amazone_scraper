"""Vue console : affichage des produits et des statistiques."""
from app.models.produit import Produit


class ConsoleView:
    def __init__(self, devise: str = ""):
        self.devise = devise

    def message(self, texte: str) -> None:
        print(texte)

    def afficher_produits(self, produits: list[Produit], limite: int = 10) -> None:
        print(f"\n=== Aperçu ({min(limite, len(produits))} sur {len(produits)} produits, "
              f"prix en {self.devise or 'devise du site'}) ===")
        for produit in produits[:limite]:
            print(produit)

    def afficher_statistiques(self, stats: dict) -> None:
        print("\n=== Statistiques ===")
        print(f"Produits scrapés : {stats['total']}")
        print(f"1) Prix moyen    : {stats['prix_moyen']:.2f} {self.devise}")
        cher = stats["plus_cher"]
        if cher:
            print(f"2) Prix maximum  : {cher.prix:.2f} {self.devise}  ({cher.titre[:60]}, {cher.categorie})")
        print("3) Nombre par catégorie :")
        for categorie, nombre in stats["par_categorie"].items():
            print(f"   - {categorie:<20} {nombre}")