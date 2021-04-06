run:
	python3 bench.py
build:
	cythonize -3 -a -f -i test.py
clean:
	rm -f test.cpython*.so
