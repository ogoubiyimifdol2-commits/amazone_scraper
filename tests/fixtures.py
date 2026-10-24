"""Faux site (mêmes structures HTML que books.toscrape.com) pour tester hors-ligne."""

BASE = "https://books.toscrape.com/"

ACCUEIL = """
<html><body>
<div class="side_categories"><ul class="nav nav-list"><li><a href="catalogue/category/books_1/index.html">Books</a>
<ul>
<li><a href="catalogue/category/books/travel_2/index.html">
    Travel
</a></li>
<li><a href="catalogue/category/books/mystery_3/index.html">
    Mystery
</a></li>
<li><a href="catalogue/category/books/science-fiction_16/index.html">
    Science Fiction
</a></li>
</ul></li></ul></div>
</body></html>
"""


def _fiche(slug: str, titre: str, prix: str, note: str, stock: str = "In stock") -> str:
    return f"""
<article class="product_pod">
  <p class="star-rating {note}"></p>
  <h3><a href="../../../{slug}/index.html" title="{titre}">{titre[:20]}...</a></h3>
  <div class="product_price">
    <p class="price_color">{prix}</p>
    <p class="instock availability"><i class="icon-ok"></i>
        {stock}
    </p>
  </div>
</article>"""


def page(fiches: list[str], suivante: str | None = None) -> str:
    nav = f'<ul class="pager"><li class="next"><a href="{suivante}">next</a></li></ul>' if suivante else ""
    return f"<html><body><ol>{''.join(fiches)}</ol>{nav}</body></html>"


PAGES = {
    BASE: ACCUEIL,
    BASE + "catalogue/category/books/travel_2/index.html": page([
        _fiche("it-happened_1", "It Happened in Italy", "Â£10.00", "Two"),
        _fiche("neither_2", "Neither Here nor There", "£38.95", "Three"),
    ]),
    BASE + "catalogue/category/books/mystery_3/index.html": page([
        _fiche("sharp_3", "Sharp Objects", "£47.82", "Four"),
    ], suivante="page-2.html"),
    BASE + "catalogue/category/books/mystery_3/page-2.html": page([
        _fiche("gone_4", "Gone Girl", "£20.00", "Five", stock="Out of stock"),
    ]),
    BASE + "catalogue/category/books/science-fiction_16/index.html": page([
        _fiche("dune_5", "Dune", "£12.00", "One"),
        _fiche("neuro_6", "Neuromancer", "£30.50", "Five"),
        _fiche("found_7", "Foundation", "£22.00", "Four"),
    ]),
}


class FauxClient:
    """Remplace ClientHTTP : sert les pages ci-dessus sans réseau ni pause."""
    delai = 0

    def __init__(self):
        self.urls_demandees: list[str] = []

    def get(self, url: str) -> str:
        self.urls_demandees.append(url)
        return PAGES[url]