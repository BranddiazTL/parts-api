install:
	pip install poetry && poetry install

check:
	poetry run ruff . && poetry run mypy . && poetry run bandit -r .

format:
	poetry run ruff check . --fix

migrate:
	poetry run alembic upgrade head

makemigration:
	poetry run alembic revision --autogenerate -m "$(name)"

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

commit:
	@echo "Enter files to add (or '.' for all):"
	@read files; git add $$files && poetry run cz commit && poetry run cz bump
