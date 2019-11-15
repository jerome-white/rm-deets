import sys
import csv
import random
import string

import phonenumbers

def rstring(vals, k):
    return ''.join(map(str, random.choices(vals, k=k)))

def getnum(no=None):
    formats = [
        'E164',
        'NATIONAL',
        'INTERNATIONAL',
        'RFC3966',
    ]
    if no is None:
        no = rstring(list(range(2, 10)), 10)
    ph = phonenumbers.parse(no, 'IN')
    fmt = getattr(phonenumbers.PhoneNumberFormat, random.choice(formats))

    return phonenumbers.format_number(ph, fmt)

fieldnames = [
    'Name',
    'Mobile',
    'Mobile 2',
]
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
writer.writeheader()

number = None
for _ in range(10):
    values = [
        rstring(string.ascii_letters, random.randrange(3, 15)),
    ]

    for _ in range(2):
        number = None if random.uniform(0, 1) > 0.7 else number
        number = getnum(number)
        values.append(number)
    writer.writerow(dict(zip(fieldnames, values)))
