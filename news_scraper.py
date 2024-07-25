import os
import re
import logging
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

class NewsScraper:
    def __init__(self, config):
        self.config = config
        self.driver = webdriver.Chrome()
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        try:
            self.open_site()
            self.search_news()
            self.scrape_news()
        finally:
            self.driver.quit()

    def open_site(self):
        self.driver.get(self.config.site_url)
        self.logger.info(f"Opened site: {self.config.site_url}")

    def search_news(self):
        # Clicking on search button
        search_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ps-header/header/div[2]/button'))  # Ajuste o XPath
        )
        search_box.click()
        input_box = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ps-header/header/div[2]/div[2]/form/label/input'))  # Ajuste o XPath
        )
        input_box.send_keys(self.config.search_phrase)
        input_box.submit()
        self.logger.info(f"Searched for phrase: {self.config.search_phrase}")

    def scrape_news(self):
        #collecting news with correct datetime
        news_data = []
        current_date = datetime.now()
        for i in range(self.config.months):
            target_date = current_date - timedelta(days=i*30)
            target_date_month = target_date.month
            self.logger.info(f"Scraping news for date: {target_date.strftime('%Y-%m')}")

            articles = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ps-promo'))  # Ajuste o seletor
            )
            for article in articles:
                
                date_str = article.find_element(By.CLASS_NAME, "promo-timestamp").text
                try:
                    
                    article_date = datetime.strptime(date_str, "%B %d, %Y")  # Formato "July 8, 2024"
                    article_date_month = article_date.month
                except ValueError:
                    
                    self.logger.error(f"Date format error: {date_str}")
                    continue
                
                if article_date_month == target_date_month:
                    title = article.find_element(By.CSS_SELECTOR, "h3").text
                    description = article.find_element(By.CLASS_NAME, "promo-description").text if article.find_elements(By.CLASS_NAME, "promo-description") else "No description"
                    
                    image_url = article.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
                    image_filename = self.download_image(image_url, title)
                    phrase_count = self.count_search_phrase(title, description)
                    contains_money = self.contains_money(title, description)
                    
                    news_data.append([title, date_str, description, image_filename, phrase_count, contains_money])

        self.save_to_excel(news_data)

    def download_image(self, url, title):
        # Removing invalid characters
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)  # Remove caracteres inválidos
        local_filename = os.path.join(self.config.output_dir, f"{safe_title}.jpg")
        
        # Downloading image
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        
        return local_filename

    def count_search_phrase(self, title, description):
        # Counting search phrase
        return title.lower().count(self.config.search_phrase.lower()) + description.lower().count(self.config.search_phrase.lower())

    def contains_money(self, title, description):
        # Counting money in article
        money_pattern = r'\$\d+(\.\d{1,2})?|\d+(\,\d{3})*(\.\d{1,2})?|(\d+|\d{1,3})\s*(dollars|USD|usd)'
        return bool(re.search(money_pattern, title, re.IGNORECASE)) or bool(re.search(money_pattern, description, re.IGNORECASE))

    def save_to_excel(self, data):
        # Saving to excel
        df = pd.DataFrame(data, columns=["Title", "Date", "Description", "Image Filename", "Phrase Count", "Contains Money"])
        output_file = os.path.join(self.config.output_dir, 'news_data.xlsx')
        df.to_excel(output_file, index=False)
        self.logger.info(f"Saved news data to Excel file: {output_file}")
