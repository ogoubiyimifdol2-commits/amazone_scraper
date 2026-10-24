"""Vue d'export : enregistrement des produits en CSV."""
import csv
from pathlib import Path

from app.models.produit import Produit

COLONNES = ["titre", "prix", "en_stock", "note", "categorie", "url"]


class ExportView:
    def exporter_csv(self, produits: list[Produit], chemin) -> Path:
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        # utf-8-sig : Excel affiche correctement les accents
        with open(chemin, "w", newline="", encoding="utf-8-sig") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=COLONNES)
            ecrivain.writeheader()
            for produit in produits:
                ecrivain.writerow(produit.en_dict())
        return chemin