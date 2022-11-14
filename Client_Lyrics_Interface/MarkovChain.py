import re
from collections import defaultdict
import random


class MarkovChain:
    def __init__(self, corpus='', starting_words='', order=2, length=8):
        self.order = order
        self.length = length
        self.words = re.findall("[a-z]+[']*[a-z]+", corpus.lower())
        self.starting_words = starting_words
        self.states = defaultdict(list)

        for i in range(len(self.words) - self.order):
            self.states[tuple(self.words[i:i + self.order])
                        ].append(self.words[i + self.order])

    def gen_sentence(self, length=8, startswith=None):
        terms = None
        if startswith:
            start_seed = [x for x in self.states.keys() if startswith in x]
            if start_seed:
                terms = list(start_seed[0])
        if terms is None:
            start_seed = random.randint(0, len(self.words) - self.order)
            terms = self.words[start_seed:start_seed + self.order]

        for _ in range(length):
            terms.append(random.choice(
                self.states[tuple(terms[-self.order:])]))

        return ' '.join(terms)

    def gen_song(self, lines=10, length=8, length_range=None):
        song = []
        if self.starting_words:
            song.append(self.gen_sentence(
                length=length, startswith=self.starting_words))
            lines -= 1
        for _ in range(lines):
            sent_len = random.randint(
                *length_range) if length_range else length
            song.append(self.gen_sentence(length=sent_len))

        return '\n'.join(song)
