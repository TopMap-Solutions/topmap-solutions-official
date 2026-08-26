.PHONY: run migrate

run:
	uv run manage.py runserver


migrate:
	uv run  manage.py makemigrations
	uv run  manage.py migrate
	uv run  manage.py showmigrations


tests:
	uv run manage.py test


db:
	uv run manage.py dbshell


shell: 
	uv run manage.py shell


lint:
	uv run djlint . --reformat

