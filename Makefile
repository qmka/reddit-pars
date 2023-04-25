install:
	poetry install

lint:
	poetry run flake8 reddit_img_parser

selfcheck:
	poetry check

check: selfcheck test lint

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl --force-reinstall

.PHONY: install test lint selfcheck check build

start:
	poetry run reddit-img-parser -r wallpapers
