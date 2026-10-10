import scrapy


class BookStoreSpider(scrapy.Spider):
    name = "bookstore"

    start_urls = ["https://aryanaghalam.com/shop/"]

    def parse(self, response):
        urls = response.css("article.product-item h3 a::attr(href)").getall()
        for url in urls:
            yield response.follow(url, callback=self.parse_book_details)
        next_page = response.css("a.next.page-numbers::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_details(self, response):
        title = response.css("h1.product_title::text").get()
        author = response.css(
            "tr.woocommerce-product-attributes-item--attribute_pa_author-name td.woocommerce-product-attributes-item__value p::text"
        ).get()
        isbn = response.xpath("//tr[contains(@class, 'woocommerce-product-attributes-item')][th[contains(text(), 'شابک')]]/td/p/text()").get()
        topic = response.css("div.product_meta span.posted_in a::text").getall()
        price = response.css(
            "div.product-simple-add-to-cart p.price span.woocommerce-Price-amount bdi::text"
        ).get()
        image_url = response.css("div.swiper-wrapper a::attr(href)").get()

        yield {
            "title": title,
            "author": author,
            "isbn": isbn,
            "topic": topic,
            "price": price,
            "image_url": image_url,
        }
