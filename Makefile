all:
	./load.py examples/grandparents.py

make:
	./load.py examples/make.py

check:
	mypy load.py

README.md: render.py logic.at
	./render.py logic.at README.md

clean:
	rm -rf __pycache__ README.md *~ .mypy_cache */__pycache__ */*~


