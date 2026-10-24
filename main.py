"""Point d'entrée : python main.py"""
from app.controllers.scraping_controller import ScrapingController


def main() -> None:
    controleur = ScrapingController.par_defaut()
    try:
        controleur.executer()
    finally:
        controleur.fermer()


if __name__ == "__main__":
    main()