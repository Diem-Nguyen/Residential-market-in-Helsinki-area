from datetime import date
from random import uniform  
import re
import time
import sys

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests

from tqdm import tqdm

today = date.today().strftime("%d/%m/%Y")

def CrawlEtuovi():
    # finding the how many pages in the website so that we can build a loop to extract all hrefs
    base_url = 'https://www.etuovi.com/myytavat-asunnot?haku=M1611624698&sivu=2'
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    page = soup.find_all('button', attrs={'data-react-toolbox':'button', 
                                   'class':'theme__button__1YqFK theme__flat__13aFK theme__button__1YqFK theme__squared__17Uvn theme__neutral__1F1Jf Button__button__3K-jn Pagination__button__3H2wX'})

    page = [int(i.get_text()) for i in page]
    max_page = max(page) # this is our max page number
    print(f'There are {max_page} pages we need to loop over in order to get hrefs')
    # find href in the each page so we can go to specific advertisement to crawl all the details.
    unit_pages =[] 
    for i in tqdm(range(1, max_page)):
        url = f'https://www.etuovi.com/myytavat-asunnot?haku=M1611624698&sivu={i}'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        links_with_text = [a['href'] for a in soup.find_all('a', href=True) if a.text]
        unit_pages.extend(links_with_text)
        time.sleep(uniform(0.2, 1.5))

    # filter only relevant href and contact the domain names
    all_pages = list(set(['https://www.etuovi.com'+page for page in unit_pages if 'kohde' in page]))
    print(f'There are {len(all_pages)} advertisements. We will go through each advertisement and extract details.')

    # establish a list to store our result
    results = []
    for page in tqdm(all_pages):
        # send a request
        r = requests.get(page)
        soup = BeautifulSoup(r.content, 'html.parser')

        # extract title and value of the html results: property characteristics
        k = soup.find_all('div', class_="flexboxgrid__col-xs-12__1I1LS flexboxgrid__col-sm-4__3RH7g ItemHeader__itemHeader__32xAv")
        v = soup.find_all('div', class_="CompactInfoRow__infoRow__2hjs_ flexboxgrid__row__wfmuy")
        k = [i.get_text() for i in k]
        v = [i.get_text() for i in v]

        # extract property price
        p = soup.find_all('div',class_='flexboxgrid__col-xs-4__p2Lev flexboxgrid__col-sm-3__28H0F flexboxgrid__col-md-5__3SFMx')
        price = [i.get_text() for i in p]
        price = [re.sub('Hinta|\xa0', '', str(i)) for i in price]

        # extract result to dictionary
        row = {k[i]: v[i] for i in range(len(k))} 
        row['price'] = price
        results.append(row)

        time.sleep(uniform(0.2, 2))

    # save to dataframe
    df = pd.DataFrame(results)
    df['date_scrape'] = today
    df.to_csv('../../data/raw/listing_price.csv', index=False)
    
    
if __name__ == "__main__":
    start_time = time.time()
    CrawlEtuovi()
    
    print("--- %s minutes ---" % ((time.time() - start_time)/60))
    

