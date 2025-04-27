from datetime import datetime, timedelta
import requests
import json
from base_scraper import BaseScraper


class DoxxbetScraper(BaseScraper):
    def __init__(self):
        super().__init__("doxxbet")
        self.api_url = ""
        self.headers = {}
        self.sport_codes = set()

    def get_dates(self, days=4):
        """Generate dates for scraping"""
        pass

    def scrape(self):
        """Scrape data from the Doxxbet API"""
        pass

    def parse(self, raw_data):
        """Parse raw data into structured output"""
        pass

