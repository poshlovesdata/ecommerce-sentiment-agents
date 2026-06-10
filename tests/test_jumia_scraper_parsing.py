"""Parser tests based on observed Jumia page structure."""

from jumia_aspect_agents.data_collection.scraper import JumiaReviewScraper, ScraperConfig
from jumia_aspect_agents.models.reviews import ProductSummary


def make_scraper() -> JumiaReviewScraper:
    return JumiaReviewScraper(
        ScraperConfig(
            category_url="https://www.jumia.com.ng/mobile-accessories/",
            min_delay_seconds=0,
            max_delay_seconds=0,
        )
    )


def test_parse_category_products_from_product_cards() -> None:
    html = """
    <html>
      <body>
        <article class="prd _fb col c-prd">
          <a class="core" href="/20000-mah-utra-slim-portable-power-bank-ace-elec-mpg11495891.html">
            <h3 class="name">Ace Elec 20000 MAh Utra Slim Portable Power Bank -Type C</h3>
            <div class="rev">3.7 out of 5 (148804)</div>
          </a>
        </article>
      </body>
    </html>
    """

    products = make_scraper().parse_category_products(html)

    assert len(products) == 1
    assert products[0].product_name == "Ace Elec 20000 MAh Utra Slim Portable Power Bank -Type C"
    assert products[0].product_url.endswith("mpg11495891.html")
    assert products[0].listing_rating == 3.7
    assert products[0].listing_review_count == 148804


def test_extract_sku_from_reviews_url() -> None:
    scraper = make_scraper()

    sku = scraper._extract_sku_from_reviews_url(  # noqa: SLF001
        "https://www.jumia.com.ng/catalog/productratingsreviews/sku/AC431EA7LKZHVNAFAMZ/"
    )

    assert sku == "AC431EA7LKZHVNAFAMZ"


def test_with_page_param_preserves_existing_query() -> None:
    scraper = make_scraper()

    url = scraper._with_page_param(  # noqa: SLF001
        "https://www.jumia.com.ng/mobile-accessories/?sort=rating",
        3,
    )

    assert url == "https://www.jumia.com.ng/mobile-accessories/?sort=rating&page=3"


def test_parse_reviews_from_visible_product_feedback_text() -> None:
    html = """
    <html>
      <body>
        <h2>Comments from Verified Purchases(32080)</h2>
        <article class="-pvs -hr _bet">
          <div>3 out of 5</div>
          <h3>powerbank</h3>
          <p>It's Portable nd very strong</p>
          <span>06-06-2026 by Raji</span>
          <span>Verified Purchase</span>
        </article>
      </body>
    </html>
    """
    product = ProductSummary(
        product_name="Ace Elec Power Bank",
        product_url="https://www.jumia.com.ng/product.html",
        sku="AC431EA7LKZHVNAFAMZ",
    )

    reviews = make_scraper().parse_reviews(html, product, source_url=product.product_url)

    assert len(reviews) == 1
    assert reviews[0].review_title == "powerbank"
    assert reviews[0].review_body == "It's Portable nd very strong"
    assert reviews[0].star_rating == 3
    assert reviews[0].review_date == "06-06-2026"
    assert reviews[0].reviewer_name == "Raji"
    assert reviews[0].verified_purchase is True
