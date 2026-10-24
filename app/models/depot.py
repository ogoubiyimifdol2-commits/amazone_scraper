"""Modèle : dépôt SQLite des produits + calcul des statistiques."""
import sqlite3
from pathlib import Path

from app.models.produit import Produit


class Depot:
    def __init__(self, chemin_db):
        self.chemin_db = str(chemin_db)
        if self.chemin_db != ":memory:":
            Path(self.chemin_db).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.chemin_db)
        self._creer_table()

    def _creer_table(self) -> None:
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS produits (
                url       TEXT PRIMARY KEY,
                titre     TEXT NOT NULL,
                prix      REAL NOT NULL,
                en_stock  INTEGER NOT NULL,
                note      REAL NOT NULL,
                categorie TEXT NOT NULL
            )"""
        )
        self._conn.commit()

    def ajouter(self, produit: Produit) -> None:
        """Insère ou met à jour (même URL = même produit, pas de doublon)."""
        self._conn.execute(
            "INSERT OR REPLACE INTO produits VALUES (?, ?, ?, ?, ?, ?)",
            (produit.url, produit.titre, produit.prix,
             int(produit.en_stock), produit.note, produit.categorie),
        )
        self._conn.commit()

    def ajouter_tous(self, produits) -> None:
        for produit in produits:
            self.ajouter(produit)

    def vider(self) -> None:
        self._conn.execute("DELETE FROM produits")
        self._conn.commit()

    def tous(self) -> list[Produit]:
        lignes = self._conn.execute(
            "SELECT titre, prix, en_stock, note, categorie, url "
            "FROM produits ORDER BY categorie, titre"
        ).fetchall()
        return [Produit(t, p, bool(s), n, c, u) for t, p, s, n, c, u in lignes]

   
    def prix_moyen(self) -> float:
        valeur = self._conn.execute("SELECT AVG(prix) FROM produits").fetchone()[0]
        return valeur or 0.0

    def produit_le_plus_cher(self) -> Produit | None:
        ligne = self._conn.execute(
            "SELECT titre, prix, en_stock, note, categorie, url "
            "FROM produits ORDER BY prix DESC LIMIT 1"
        ).fetchone()
        if ligne is None:
            return None
        t, p, s, n, c, u = ligne
        return Produit(t, p, bool(s), n, c, u)

    def nombre_par_categorie(self) -> dict[str, int]:
        lignes = self._conn.execute(
            "SELECT categorie, COUNT(*) FROM produits "
            "GROUP BY categorie ORDER BY COUNT(*) DESC, categorie"
        ).fetchall()
        return dict(lignes)

    def statistiques(self) -> dict:
        return {
            "total": sum(self.nombre_par_categorie().values()),
            "prix_moyen": self.prix_moyen(),
            "plus_cher": self.produit_le_plus_cher(),
            "par_categorie": self.nombre_par_categorie(),
        }

    def fermer(self) -> None:
        self._conn.close()