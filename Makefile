help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Poetry and all dependencies
	pip install poetry && poetry install

check: ## Run ruff, mypy, and bandit checks
	poetry run ruff . && poetry run mypy . && poetry run bandit -r .

format: ## Auto-format code with ruff
	poetry run ruff check . --fix

migrate: ## Run Alembic migrations
	poetry run alembic upgrade head

makemigration: ## Create a new Alembic migration
	poetry run alembic revision --autogenerate -m "$(name)"

docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start Docker containers
	docker compose up -d

docker-down: ## Stop Docker containers
	docker compose down

commit: ## Interactive commit with Commitizen and version bump
	@if ! git diff --quiet --exit-code; then \
		echo "Enter files to add (or '.' for all):"; \
		read files; \
		git add $$files; \
	else \
		echo "No unstaged changes to add."; \
	fi; \
	poetry run cz commit; \
	poetry run cz bump || true