py=.venv/bin/python

build:
	make clean
	make version
	$(py) -m build

version:
	$(py) version_script.py

clean:
	touch dist/fuck
	rm dist/*

upload:
	make build
	$(py) -m twine upload --repository pypi dist/* $(flags)

reload:
	make upload
	pipx upgrade auto-dlp
	pipx upgrade auto-dlp
	auto-dlp --version .
