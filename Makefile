help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install Poetry, dependencies, copy .env, and setup pre-commit
	pip install poetry && poetry install --no-root
	cp .env.example .env
	poetry run pre-commit install

check: ## Run ruff, mypy, and bandit checks
	poetry run ruff check . && poetry run mypy . && poetry run bandit -r .

format: ## Auto-format code with ruff
	poetry run ruff format .

migrate: ## Run Alembic migrations
	poetry run alembic upgrade head

makemigration: ## Create a new Alembic migration
	poetry run alembic revision --autogenerate -m "$(name)"

build: ## Build Docker images
	docker compose -p parts -f deployment/docker/docker-compose.yml build

up: ## Start Docker containers
	docker compose -p parts -f deployment/docker/docker-compose.yml up -d

down: ## Stop Docker containers
	docker compose -p parts -f deployment/docker/docker-compose.yml down

commit: ## Interactive commit with Commitizen and version bump
	@if ! git diff --quiet --exit-code; then \
		echo "Enter files to add (or '.' for all):"; \
		read files; \
		git add $$files; \
	else \
		echo "No unstaged changes to add."; \
	fi; \
	poetry run cz commit;

bump: ## Bump API versioning using SEMVER format
	poetry run cz bump || true