import random
import timeit

setup = """
from test import GlyphCoordinates
a0 = GlyphCoordinates()
a10 = GlyphCoordinates.zeros(10)
a100 = GlyphCoordinates.zeros(100)
a1000 = GlyphCoordinates.zeros(1000)
b0 = GlyphCoordinates()
b10 = GlyphCoordinates.zeros(10)
b100 = GlyphCoordinates.zeros(100)
b1000 = GlyphCoordinates.zeros(1000)
""".replace('\t', '')

def bench(stmt, number=1000, repeat=5):
	results = timeit.repeat(stmt, setup=setup, number=number, repeat=repeat)
	print('%7.2fus\t%s' % (min(results) * 1000000. / number, stmt))

def main():
	bench('GlyphCoordinates()')
	bench('GlyphCoordinates.zeros(100)')
	bench('a100 * .5')
	bench('b100 - a100')
	bench('b100 -= a100')

random.seed(1)
main()
