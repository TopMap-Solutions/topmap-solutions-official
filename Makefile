.PHONY: run migrate test test-ui lint lint-python lint-templates lint-css lint-js format

run:
	uv run manage.py runserver


migrate:
	uv run  manage.py makemigrations
	uv run  manage.py migrate
	uv run  manage.py showmigrations


test:
	uv run manage.py test --settings=config.settings.test


db:
	uv run manage.py dbshell


shell: 
	uv run manage.py shell


lint:
	$(MAKE) lint-python
	$(MAKE) lint-templates
	$(MAKE) lint-css
	$(MAKE) lint-js


lint-python:
	uv run --frozen ruff check .


lint-templates:
	uv run --frozen djlint . --profile=django --check


lint-css:
	npm run lint:css


lint-js:
	npm run lint:js


format:
	uv run --frozen ruff check . --fix
	uv run --frozen ruff format .
	uv run --frozen djlint . --profile=django --reformat
	npm run format:css
	npm run format:js


test-ui:
	uv run --frozen python -B -m django test apps.guests.tests.test_public_site --settings=config.settings.test_ui
