import csv
import itertools as it
import functools as ft
import collections as cl
from pathlib import Path
from argparse import ArgumentParser

from util import Logger, Anonymizer, MobileAnonymizer

Columns = cl.namedtuple('Columns', 'standard, mobile')

class Transcriber:
    def __init__(self, translator):
        self.translator = translator

    def do(self, row):
        for (k, v) in row.items():
            if k in self.translator:
                v = v.strip().lower()
                if v:
                    v = self.translator[k][v]
            yield (k, v)

    def transcribe(self, path):
        with path.open() as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                yield dict(self.do(row))

def mktranslator(ctypes, args):
    instances = {}

    for (k, v) in ctypes._asdict().items():
        columns = getattr(args, k + '_column')
        if columns:
            if k not in instances:
                instances[k] = v()
            inst = instances[k]
            for i in columns:
                yield (i, inst)

arguments = ArgumentParser()
arguments.add_argument('--logs', type=Path)
arguments.add_argument('--country-code', type=int, default=91)
arguments.add_argument('--extension', default='-anon')
for i in Columns._fields:
    option = '--{}-column'.format(i)
    arguments.add_argument(option, action='append')
args = arguments.parse_args()

ctypes = Columns(standard=Anonymizer,
                 mobile=ft.partial(MobileAnonymizer, args.country_code))
tr = Transcriber(dict(mktranslator(ctypes, args)))

condition = lambda x: x.stem.endswith(args.extension)
for i in it.filterfalse(condition, args.logs.rglob('*.csv')):
    Logger.info(i)

    fname = '{}{}'.format(i.stem, args.extension)
    output = i.parent.joinpath(fname).with_suffix(i.suffix)
    if output.exists():
        Logger.warning('Overwritting {}'.format(output))

    with output.open('w') as fp:
        writer = None
        for row in tr.transcribe(i):
            if writer is None:
                writer = csv.DictWriter(fp, fieldnames=row.keys())
                writer.writeheader()
            writer.writerow(row)
