"""Client HTTP poli : User-Agent identifiable, robots.txt, pause entre requêtes."""
import time
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests


class ErreurScraping(Exception):
    """Erreur levée quand une page ne peut pas (ou ne doit pas) être récupérée."""


class ClientHTTP:
    def __init__(self, user_agent: str, delai: float, timeout: float):
        self.delai = delai
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self._user_agent = user_agent
        self._robots: dict[str, robotparser.RobotFileParser] = {}
        self._derniere_requete = 0.0

    # --- robots.txt --------------------------------------------------------
    def _lire_robots(self, url: str) -> robotparser.RobotFileParser:
        origine = "{0.scheme}://{0.netloc}".format(urlparse(url))
        if origine not in self._robots:
            parseur = robotparser.RobotFileParser()
            try:
                reponse = self._session.get(urljoin(origine, "/robots.txt"), timeout=self.timeout)
                if reponse.status_code == 200:
                    parseur.parse(reponse.text.splitlines())
                else:  # pas de robots.txt : tout est autorisé
                    parseur.parse([])
            except requests.RequestException:
                parseur.parse([])
            self._robots[origine] = parseur
        return self._robots[origine]

    def est_autorise(self, url: str) -> bool:
        return self._lire_robots(url).can_fetch(self._user_agent, url)

    # --- téléchargement ----------------------------------------------------
    def _attendre(self) -> None:
        ecoule = time.monotonic() - self._derniere_requete
        if ecoule < self.delai:
            time.sleep(self.delai - ecoule)

    def _telecharger(self, url: str) -> str:
        try:
            reponse = self._session.get(url, timeout=self.timeout)
            reponse.raise_for_status()
        except requests.RequestException as erreur:
            raise ErreurScraping(f"Échec du téléchargement de {url} : {erreur}") from erreur
        reponse.encoding = "utf-8"  # évite « Â£ » à la place de « £ »
        return reponse.text

    def get(self, url: str) -> str:
        if not self.est_autorise(url):
            raise ErreurScraping(f"robots.txt interdit l'accès à {url}")
        self._attendre()
        try:
            return self._telecharger(url)
        finally:
            self._derniere_requete = time.monotonic()

    def fermer(self) -> None:
        self._session.close()


class ClientSelenium(ClientHTTP):
    """Même interface que ClientHTTP, mais via Chrome (exécute le JavaScript).
    Respecte robots.txt et les pauses ; ne cherche pas à masquer l'automatisation."""

    def __init__(self, user_agent: str, delai: float, timeout: float,
                 headless: bool = True, selecteur_attente: str | None = None):
        super().__init__(user_agent, delai, timeout)
        self.headless = headless
        self.selecteur_attente = selecteur_attente
        self._pilote = None

    def _obtenir_pilote(self):
        if self._pilote is None:
            from selenium import webdriver  # import tardif : selenium reste optionnel
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument(f"--user-agent={self._user_agent}")
            self._pilote = webdriver.Chrome(options=options)
            self._pilote.set_page_load_timeout(self.timeout)
        return self._pilote

    def _telecharger(self, url: str) -> str:
        from selenium.common.exceptions import TimeoutException, WebDriverException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        from urllib3.exceptions import HTTPError
        try:
            pilote = self._obtenir_pilote()
            try:
                pilote.get(url)
            except TimeoutException:
                pilote.execute_script("window.stop()")  # page trop lente : on garde ce qui est chargé
            if self.selecteur_attente:
                try:
                    WebDriverWait(pilote, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.selecteur_attente)))
                except TimeoutException:
                    pass  # on renvoie la page telle quelle (CAPTCHA détecté plus haut)
            return pilote.page_source
        except (WebDriverException, HTTPError, OSError) as erreur:
            resume = (getattr(erreur, "msg", None) or str(erreur)).strip().splitlines()[0]
            raise ErreurScraping(f"Échec Selenium sur {url} : {resume}") from erreur

    def fermer(self) -> None:
        if self._pilote is not None:
            self._pilote.quit()
            self._pilote = None
        super().fermer()