import random
import string
import collections as cl

import phonenumbers as tel

class RandomWord:
    def __init__(self, maxlen, unique=False):
        self.maxlen = maxlen
        self.letters = string.ascii_letters + string.digits

        if not unique:
            self.sample = random.choices
        elif len(self.letters) > self.maxlen:
            msg = 'Maximum length of a unique word is {}'
            raise ValueError(msg.format(len(self.letters)))
        else:
            self.sample = random.sample

    def __iter__(self):
        return self

    def __next__(self):
        return ''.join(self.sample(self.letters, k=self.maxlen))

class Anonymizer:
    def __init__(self, bits=32):
        self.word = RandomWord(bits)

        self.keys = set()
        self.correspondance = cl.defaultdict(self)

    def __getitem__(self, key):
        return self.correspondance[self.parse(key)]

    def __call__(self):
        for i in self.word:
            if i not in self.keys:
                self.keys.add(i)
                return i

        raise LookupError('Cannot generate new key')

    def parse(self, key):
        return key

class MobileAnonymizer(Anonymizer):
    def __init__(self, country):
        codes = tel.region_codes_for_country_code(country)
        if not codes:
            raise ValueError('Invalid country code {}'.format(country))
        self.region = random.choice(codes)

        ph = tel.example_number(self.region)
        bits = len(str(ph.national_number)) + 1
        super().__init__(bits)

    def parse(self, key):
        ph = tel.parse(key, self.region)
        if not tel.is_possible_number(ph):
            raise ValueError('Invalid mobile number {}'.format(key))
        return ph.national_number
