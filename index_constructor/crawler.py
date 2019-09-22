import logging
import re
import os
import json
import time
import math
from text_processor import TextProcessor

from bs4 import BeautifulSoup
from collections import defaultdict

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self):
        # analytic variables
        self.start = 0
        self.end = 0
        self.counter = 0

        self.index = dict()  # index: token(doc_id(freq))

    def start_crawling(self):
        counter = 0  # counter for the number of corpuses
        # with open('WEBPAGES_RAW/bookkeeping.json', 'r') as bookkeeping: # used for crawling entire corpus
        # used for crawling only the valid corpus
        with open('bookkeeping.json', 'r') as bookkeeping:
            books = json.load(bookkeeping)
        self.start = time.time()
        for path in books:
            logger.info("Fetching URL %s", path)

            # filepath = "WEBPAGES_RAW/" + path # used for crawling entire corpus
            # with open(filepath, 'rb') as corpus:
            with open(path, 'rb') as corpus:
                content = corpus.read()

            # extracts crawlable text content from the valid url
            extracted_text = self.extract_text(content)
            # updates the index with new url content
            path = path.split("WEBPAGES_RAW")[1][1:]
            self.index = self.process(extracted_text, path)
            self.counter += 1
        self.create_tfidf()
        self.end = time.time()

    def create_tfidf(self):
        for term, postings in self.index.items():
            dft = len(postings)
            for doc_id, freq in postings.items():
                tf = 1 + math.log10(freq)
                idf = math.log10((self.counter/dft))
                postings[doc_id] = tf * idf
            

    def extract_text(self, content):
        '''
        extracts useful information from the parsed link.
        information is return as a list, including blank lines
        '''
        parsed = BeautifulSoup(content, 'lxml')
        # remove all script and style element from the html
        for script in parsed(['script', 'style']):
            script.extract()
        # parse text from the html
        text = parsed.get_text()
        # break into lines and remove leading and trailing space on each
        result = (line.strip() for line in text.splitlines())
        return result

    def process(self, text, doc_id):
        '''
        calls on the TextProcessor class for text processing and tokenization of documents.
        each url is designated with unique id number.
        id is increased at the end for new url.
        returns updated index.
        '''
        processor = TextProcessor(text, self.index, doc_id)
        processor.process_text()
        return processor.get_index()

    def export_index(self):
        '''
        exports the index dictionary into a text file (storage)
        '''
        if not os.path.exists('index'):
            os.mkdir('index')

        print("\n\n\nExporting index to /index/index.json")
        with open('index/index.json', 'w+') as index:
            index.write(json.dumps(self.index, indent=2))
        print("Export finished")

        print("\nExporting analytics to /index/analytics.txt")
        with open('index/analytics.txt', 'w+') as analytics:
            analytics.write("Number of unique terms: " +
                            str(len(self.index.keys())))
            analytics.write("\nExecution time: " +
                            str(self.end - self.start) + ' seconds')
            analytics.write("\nTotal number of documents: " +
                            str(self.counter))
        print("Export finished")
