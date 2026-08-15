.PHONY: run migrate

run:
	uv run manage.py runserver


migrate:
	uv run  manage.py makemigrations
	uv run  manage.py migrate
	uv run  manage.py showmigrations