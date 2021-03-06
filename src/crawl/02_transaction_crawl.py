import scrapy
from scrapy.crawler import CrawlerProcess
    
from datetime import date
import time

today = date.today().strftime("%d/%m/%Y")

class MySpider(scrapy.Spider):
    name = "price"
    
    custom_settings = {
    'FEED_FORMAT': 'csv',
    'FEED_URI': '../../data/raw/transaction_price.csv',
      'DOWNLOAD_DELAY': 5,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
    'CONCURRENT_REQUESTS_PER_IP': 3
}

    # concat page according to cities and page number
    cities = ['Espoo', 'Vantaa', 'Helsinki']
    start_urls = []
    for city in cities:
        for i in range (0, 100):
            url = f'https://asuntojen.hintatiedot.fi/haku/?c={city}&cr=1&t=3&l=0&z={i}&search=1&sf=0&so=a'
            start_urls.append(url)
    
    def parse(self, response):
        for url in start_urls:
            next_page = response.css('#next-prev-top').get() 
            if re.search(next_page, "seuraava sivu"): # if page contains next page, then yield request
                yield scrapy.Request(url, callback=self.parse_book)

    def parse(self, response):
        rows =  response.xpath('//*[@id="mainTable"]/tbody[2]')
        for row in rows.css('tr'):         
            yield {
                'district' : row.xpath('td[1]/text()').get(),
                'apartment_type' : row.xpath('td[2]/text()').get(),
                'property_type' : row.xpath('td[3]/text()').get(),
                'floor_area' : row.xpath('td[4]/text()').get(),
                'price' : row.xpath('td[5]/text()').get(),                
                'price_m2' : row.xpath('td[6]/text()').get(),
                'build_year' : row.xpath('td[7]/text()').get(),
                'floor' : row.xpath('td[8]/text()').get(),
                'elevator' : row.xpath('td[9]/text()').get(),
                'condition' : row.xpath('td[10]/text()').get(),
                'plot' : row.xpath('td[11]/text()').get(),
                'energy_class': row.xpath('td[12]/text()').get(),
                'date_scrape': today,
                'municipaliy': response.url
            }
            
if __name__ == "__main__":
    start_time = time.time()
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(MySpider)
    process.start() # the script will block here until the crawling is finished
    print("--- %s seconds ---" % (time.time() - start_time))
            
#\Users\user\Good-place-to-buy-a-property-in-Helsinki-area\src\price_spider>scrapy crawl price    
            