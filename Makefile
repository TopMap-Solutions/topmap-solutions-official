.PHONY: run migrate test-ui

run:
	uv run manage.py runserver


migrate:
	uv run  manage.py makemigrations
	uv run  manage.py migrate
	uv run  manage.py showmigrations


test:
	uv run manage.py test


db:
	uv run manage.py dbshell


shell: 
	uv run manage.py shell


lint:
	uv run djlint . --reformat


test-ui:
	uv run --frozen python -B -m django test tests --settings=config.settings.test_ui
