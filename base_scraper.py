from abc import ABC, abstractmethod

class BaseScraper(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def parse(self, raw_data):
        pass


