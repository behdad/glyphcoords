# cython: language_level=3, boundscheck=False

import array
from numbers import Number

otRound = round

class GlyphCoordinates(object):

	def __init__(self, iterable=[], typecode="h"):
		self._a = array.array(typecode)
		self.extend(iterable)

	@property
	def array(self):
		return self._a

	def isFloat(self):
		return self._a.typecode == 'd'

	def _ensureFloat(self):
		if self.isFloat():
			return
		# The conversion to list() is to work around Jython bug
		self._a = array.array("d", list(self._a))

	def _checkFloat(self, p):
		if self.isFloat():
			return p
		if any(v > 0x7FFF or v < -0x8000 for v in p):
			self._ensureFloat()
			return p
		if any(isinstance(v, float) for v in p):
			p = [int(v) if int(v) == v else v for v in p]
			if any(isinstance(v, float) for v in p):
				self._ensureFloat()
		return p

	@staticmethod
	def zeros(count):
		return GlyphCoordinates([(0,0)] * count)

	def copy(self):
		c = GlyphCoordinates(typecode=self._a.typecode)
		c._a.extend(self._a)
		return c

	def __len__(self):
		return len(self._a) // 2

	def __getitem__(self, k):
		if isinstance(k, slice):
			indices = range(*k.indices(len(self)))
			return [self[i] for i in indices]
		return self._a[2*k],self._a[2*k+1]

	def __setitem__(self, k, v):
		if isinstance(k, slice):
			indices = range(*k.indices(len(self)))
			# XXX This only works if len(v) == len(indices)
			for j,i in enumerate(indices):
				self[i] = v[j]
			return
		v = self._checkFloat(v)
		self._a[2*k],self._a[2*k+1] = v

	def __delitem__(self, i):
		i = (2*i) % len(self._a)
		del self._a[i]
		del self._a[i]

	def __repr__(self):
		return 'GlyphCoordinates(['+','.join(str(c) for c in self)+'])'

	def append(self, p):
		p = self._checkFloat(p)
		self._a.extend(tuple(p))

	def extend(self, iterable):
		for p in iterable:
			p = self._checkFloat(p)
			self._a.extend(p)

	def toInt(self, *, round=otRound):
		if not self.isFloat():
			return
		a = array.array("h")
		for n in self._a:
			a.append(round(n))
		self._a = a

	def relativeToAbsolute(self):
		a = self._a
		x,y = 0,0
		for i in range(len(a) // 2):
			x = a[2*i  ] + x
			y = a[2*i+1] + y
			self[i] = (x, y)

	def absoluteToRelative(self):
		a = self._a
		x,y = 0,0
		for i in range(len(a) // 2):
			dx = a[2*i  ] - x
			dy = a[2*i+1] - y
			x = a[2*i  ]
			y = a[2*i+1]
			self[i] = (dx, dy)

	def translate(self, p):
		"""
		>>> GlyphCoordinates([(1,2)]).translate((.5,0))
		"""
		(x,y) = self._checkFloat(p)
		a = self._a
		for i in range(len(a) // 2):
			self[i] = (a[2*i] + x, a[2*i+1] + y)

	def scale(self, p):
		"""
		>>> GlyphCoordinates([(1,2)]).scale((.5,0))
		"""
		(x,y) = self._checkFloat(p)
		a = self._a
		for i in range(len(a) // 2):
			self[i] = (a[2*i] * x, a[2*i+1] * y)

	def transform(self, t):
		"""
		>>> GlyphCoordinates([(1,2)]).transform(((.5,0),(.2,.5)))
		"""
		a = self._a
		for i in range(len(a) // 2):
			x = a[2*i  ]
			y = a[2*i+1]
			px = x * t[0][0] + y * t[1][0]
			py = x * t[0][1] + y * t[1][1]
			self[i] = (px, py)

	def __eq__(self, other):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g2 = GlyphCoordinates([(1.0,2)])
		>>> g3 = GlyphCoordinates([(1.5,2)])
		>>> g == g2
		True
		>>> g == g3
		False
		>>> g2 == g3
		False
		"""
		if type(self) != type(other):
			return NotImplemented
		return self._a == other._a

	def __ne__(self, other):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g2 = GlyphCoordinates([(1.0,2)])
		>>> g3 = GlyphCoordinates([(1.5,2)])
		>>> g != g2
		False
		>>> g != g3
		True
		>>> g2 != g3
		True
		"""
		result = self.__eq__(other)
		return result if result is NotImplemented else not result

	# Math operations

	def __pos__(self):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g
		GlyphCoordinates([(1, 2)])
		>>> g2 = +g
		>>> g2
		GlyphCoordinates([(1, 2)])
		>>> g2.translate((1,0))
		>>> g2
		GlyphCoordinates([(2, 2)])
		>>> g
		GlyphCoordinates([(1, 2)])
		"""
		return self.copy()
	def __neg__(self):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g
		GlyphCoordinates([(1, 2)])
		>>> g2 = -g
		>>> g2
		GlyphCoordinates([(-1, -2)])
		>>> g
		GlyphCoordinates([(1, 2)])
		"""
		r = self.copy()
		a = r._a
		for i in range(len(a)):
			a[i] = -a[i]
		return r
	def __round__(self, *, round=otRound):
		r = self.copy()
		r.toInt(round=round)
		return r

	def __add__(self, other): return self.copy().__iadd__(other)
	def __sub__(self, other): return self.copy().__isub__(other)
	def __mul__(self, other): return self.copy().__imul__(other)
	def __truediv__(self, other): return self.copy().__itruediv__(other)

	__radd__ = __add__
	__rmul__ = __mul__
	def __rsub__(self, other): return other + (-self)

	def __iadd__(self, other):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g += (.5,0)
		>>> g
		GlyphCoordinates([(1.5, 2.0)])
		>>> g2 = GlyphCoordinates([(3,4)])
		>>> g += g2
		>>> g
		GlyphCoordinates([(4.5, 6.0)])
		"""
		if isinstance(other, tuple):
			assert len(other) ==  2
			self.translate(other)
			return self
		if isinstance(other, GlyphCoordinates):
			if other.isFloat(): self._ensureFloat()
			other = other._a
			a = self._a
			assert len(a) == len(other)
			for i in range(len(a) // 2):
				self[i] = (a[2*i] + other[2*i], a[2*i+1] + other[2*i+1])
			return self
		return NotImplemented

	def __isub__(self, other):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g -= (.5,0)
		>>> g
		GlyphCoordinates([(0.5, 2.0)])
		>>> g2 = GlyphCoordinates([(3,4)])
		>>> g -= g2
		>>> g
		GlyphCoordinates([(-2.5, -2.0)])
		"""
		if isinstance(other, tuple):
			assert len(other) ==  2
			self.translate((-other[0],-other[1]))
			return self
		if isinstance(other, GlyphCoordinates):
			if other.isFloat(): self._ensureFloat()
			other = other._a
			a = self._a
			assert len(a) == len(other)
			for i in range(len(a) // 2):
				self[i] = (a[2*i] - other[2*i], a[2*i+1] - other[2*i+1])
			return self
		return NotImplemented

	def __imul__(self, other):
		"""
		>>> g = GlyphCoordinates([(1,2)])
		>>> g *= (2,.5)
		>>> g *= 2
		>>> g
		GlyphCoordinates([(4.0, 2.0)])
		>>> g = GlyphCoordinates([(1,2)])
		>>> g *= 2
		>>> g
		GlyphCoordinates([(2, 4)])
		"""
		if isinstance(other, Number):
			other = (other, other)
		if isinstance(other, tuple):
			if other == (1,1):
				return self
			assert len(other) ==  2
			self.scale(other)
			return self
		return NotImplemented

	def __itruediv__(self, other):
		"""
		>>> g = GlyphCoordinates([(1,3)])
		>>> g /= (.5,1.5)
		>>> g /= 2
		>>> g
		GlyphCoordinates([(1.0, 1.0)])
		"""
		if isinstance(other, Number):
			other = (other, other)
		if isinstance(other, tuple):
			if other == (1,1):
				return self
			assert len(other) ==  2
			self.scale((1./other[0],1./other[1]))
			return self
		return NotImplemented

	def __bool__(self):
		"""
		>>> g = GlyphCoordinates([])
		>>> bool(g)
		False
		>>> g = GlyphCoordinates([(0,0), (0.,0)])
		>>> bool(g)
		True
		>>> g = GlyphCoordinates([(0,0), (1,0)])
		>>> bool(g)
		True
		>>> g = GlyphCoordinates([(0,.5), (0,0)])
		>>> bool(g)
		True
		"""
		return bool(self._a)

	__nonzero__ = __bool__
