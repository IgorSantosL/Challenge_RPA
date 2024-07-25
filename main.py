import logging
from news_scraper import NewsScraper
from config import Config

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Configuration Parameters
    config = Config(
        site_url="https://www.latimes.com/",
        search_phrase="technology",
        news_category="top",
        months=3
    )
    scraper = NewsScraper(config)
    scraper.run()

if __name__ == "__main__":
    main()
