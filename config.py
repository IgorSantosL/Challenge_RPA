import os

class Config:
    def __init__(self, site_url, search_phrase, news_category, months):
        self.site_url = site_url
        self.search_phrase = search_phrase
        self.news_category = news_category
        self.months = months
        self.output_dir = "./output"
        os.makedirs(self.output_dir, exist_ok=True)
