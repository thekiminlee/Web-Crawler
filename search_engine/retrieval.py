import logging
import json
import os

from collections import defaultdict


class Retrieval:
    ''' 
        Class responsible for retrieving user's search query and returning refined search result with tf-idf ranking
        Class can be initiated with [terminal, web interface]
    '''

    def __init__(self):
        '''
            Initializes all the necessary variable for retrieving information.
            Two json files are loaded -> index and bookkeeping
        '''
        self.results = defaultdict(float) # search result with value as tf-idf. Unordered
        self.query = "" # Users search query
        self.total = 0 # Total number of search results. Length of self.results
        self.search_result = [] # Minimized list of search result. 
        self.threshold = 30 # Threshold limiting the number of url displayed to the user
        with open('search_engine/json/index.json', 'r') as index:
            self.index = json.load(index)

        with open('search_engine/json/bookkeeping.json', 'r') as bookkeeping:
            self.books = json.load(bookkeeping)

    def prompt_user(self, query):
        '''
            Accepts user query and split it to check for multi-term query
            Passes each term to search() for information retrieval
        '''
        self.query = query
        for sub_query in query.lower().split(" "):
            self.search(sub_query)

    def search(self, query):
        '''
            Accepts single term from prompt_user() and retrieves corresponding posting for the term.
            Updates self.results dictionary with doc_id and corresponding tf-idf for ranking
        '''
        try:
            postings = self.index[query]
            for doc_id, tf_idf in postings.items():
                self.results[doc_id] += tf_idf
        except KeyError:
            pass

    def refine_query(self):
        '''
            If user's query does yield a result, sort the result by ranking.
            self.search_result is set to keys (doc_id) of sorted dictionary
        '''
        if self.results:  
            sorted_result = dict(sorted(self.results.items(), key=lambda kv: -kv[1]))
            self.search_result = list(sorted_result.keys())

    def display(self):
        '''
            display function for CLI
            Prints first <threshold> url for the given query
        '''
        self.total = len(self.search_result)
        print("The query '" + self.query + "' had " + str(self.total) +
              " results (displaying first 20):\n")

        display_counter = self.total
        if self.total > self.threshold:
            display_counter = self.threshold
        for i in range(0, display_counter):
            url = './WEBPAGES_RAW/' + self.search_result[i]
            print("\t" + self.books[url] \
            # + '\t' + str(self.results[self.search_result[i]]) \
            )
        print("\n")
        self.refresh()

    def display_web(self):
        '''
            display function for web interface
            returns tuple of first <threshold> url for the given query and user query information
        '''
        search_results = []
        result_info = dict()

        self.total = len(self.search_result)
        result_info['query'] = self.query
        result_info['total'] = self.total

        display_counter = self.total
        if self.total > self.threshold:
            display_counter = self.threshold
        for i in range(0, display_counter):
            url = './WEBPAGES_RAW/' + self.search_result[i]
            search_results.append(self.books[url])
        self.refresh()

        return (search_results, result_info, len(search_results))

    def refresh(self):
        '''
            resets current query state to 0
        '''
        self.results.clear()
        self.query = ""
        self.total = 0
        self.search_result = []

    def export_result(self):
        if not os.path.exists('analytics'):
            os.mkdir('analytics')

        with open('analytics/analytic_v2.txt', 'a+') as analytic:
            analytic.write("The query '" + self.query + "' had " + str(self.total) +
                           " results (displaying first 20):\n")
            for i in range(0, 20):
                analytic.write("\t" + self.search_result[i] + '\n')
            analytic.write("\n")


if __name__ == '__main__':
    retrieval = Retrieval()
    query = input("Enter search query: ")
    while(query.lower() != 'quit()'):
        retrieval.prompt_user(query)
        retrieval.refine_query()
        retrieval.display()
        # retrieval.export_result()
        query = input("Enter search query: ")
