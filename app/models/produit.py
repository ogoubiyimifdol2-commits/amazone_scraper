"""Modèle : un produit scrapé (livre ou article Amazon)."""
from dataclasses import dataclass, asdict


@dataclass
class Produit:
    titre: str
    prix: float          
    en_stock: bool
    note: float          
    categorie: str
    url: str

    def en_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        stock = "en stock" if self.en_stock else "rupture"
        return f"{self.titre[:45]:<45} | {self.prix:>9.2f} | {self.note:.1f}★ | {stock}"