import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
    
from datetime import date
import time

today = date.today().strftime("%d/%m/%Y")

class RentSpider(scrapy.Spider):
    name = "rent"
    # load lsiting price file that contains list of postcodes that we are interested in
    df = pd.read_csv('../../data/processed/listing_price.csv', sep=';')
    df['postcode'] = df['postcode'].astype(str).str.pad(width=5, side='left', fillchar='0')
    
    custom_settings = {
    'FEED_FORMAT': 'csv',
    'FEED_URI': '../../data/raw/transaction_rent.csv',# location where the output file is saved
     'DOWNLOAD_DELAY': 5,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
    'CONCURRENT_REQUESTS_PER_IP': 3
}
    
    # find rent where transaction prices are available
    postcode_list = df['postcode'].unique() 
    start_urls = [
       f"https://asuntojen.hintatiedot.fi/haku/vuokratiedot?c=&ps={postcode}&renderType=renderTypeTable" for postcode in postcode_list
    ]

    def parse(self, response):
        for i in range(2, 7):
            rows =  response.xpath(f'//*[@id="mainTable"]/tbody/tr[{i}]')      
            for row in rows:
                yield {
                    'postcode': response.xpath(' /html/body/div/div[4]/table/tbody/tr[1]/td/strong/text()').get(),
                    'apartment_type' : row.xpath('td[1]/text()').get(),
                    'ARA_rental' : row.xpath('td[2]/text()').get(),
                    'nonsub_old' : row.xpath('td[3]/text()').get(),
                    'nonsub_new' : row.xpath('td[4]/text()').get()            
                }

#//*[@id="mainTable"]/tbody/tr[3]
if __name__ == "__main__":
    start_time = time.time()
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(RentSpider)
    process.start() # the script will block here until the crawling is finished
    print("--- %s seconds ---" % (time.time() - start_time))       
    
#crapy crawl rent  -o ../../../../data/rent.jl