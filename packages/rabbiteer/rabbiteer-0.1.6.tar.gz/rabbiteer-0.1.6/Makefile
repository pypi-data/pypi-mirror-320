build:
	rm -rf dist
	python -m pip install --upgrade build
	python -m build

upload:
	python -m pip install --upgrade twine
	twine upload dist/*