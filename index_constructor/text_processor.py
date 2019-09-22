# python3 used
# Ki Min Lee 47872069 kmlee3

import sys
import re

from collections import defaultdict


class TextProcessor:
    def __init__(self, content, index, doc_id):
        self.content = content
        self.index = index
        self.doc_id = doc_id

    def process_text(self):
        for line in self.content:
            if line:
                for word in re.findall("[a-zA-Z0-9]+", line):
                    if(word.lower() not in self.index.keys()):
                        self.index[word.lower()] = defaultdict(float)
                    self.index[word.lower()][self.doc_id] += 1.00

    def get_index(self):
        return self.index
