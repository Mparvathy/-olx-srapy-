import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OlxSpider(scrapy.Spider):
    name = 'olx_spider'
    allowed_domains = ['olx.in']
    start_urls = [ 'https://www.olx.in/item/house-for-lease-ground-only-iid-1672646341']

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Running in headless mode
        self.driver = webdriver.Chrome(options=chrome_options)

    def close(self, spider):
        self.driver.quit()

    def parse(self, response):
        self.driver.get(response.url)

        # Wait for the first item card to appear before continuing
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='item-card']"))
        )
        while True:
            try:
                load_more_button = self.driver.find_element(By.XPATH, "//button[text()='Load more']")
                if load_more_button:
                    load_more_button.click()
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='item-card']"))
                    )
            except Exception as e:
                self.logger.debug(f"Load more button not found or end of pagination: {e}")
                break

        # Extract rental property URLs
        property_urls = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/item/')]")
        for url in property_urls:
            yield scrapy.Request(url.get_attribute('href'), callback=self.parse_rental_details)

    def parse_rental_details(self, response):
        selector = Selector(response)

        # Extract property details using XPath selectors
        property_name = selector.xpath('//h1[@class="title-36"]/text()').get()
        property_id = selector.xpath('//span[@class="item-id__data-block"]/text()').get()
        price_text = selector.xpath('//div[@class="price-section__content-8UqVQ"]//text()').getall()
        price = {'amount': price_text[0].strip(), 'currency': price_text[1].strip()}
        image_url = selector.xpath('//img[@class="item-image__img-1O2Gl"]/@src').get()
        description = ''.join(selector.xpath('//div[@class="item-desc-section__text-YmOmV"]/p/text()').getall()).strip()
        seller_name = selector.xpath('//span[@class="contact-person__name-2Sh5Z"]/text()').get()
        location = selector.xpath('//span[@class="x-location__region x-location__component x-location__component-3 a8c3a"]/text()').get().strip()

        yield {
            "property_name": property_name,
            "property_id": property_id,
            "price": price,
            "image_url": image_url,
            "description": description,
            "seller_name": seller_name,
            "location": location,
        }
