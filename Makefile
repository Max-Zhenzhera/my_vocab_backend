PROJECT_NAME := my_vocab_backend
DC := docker-compose
MIGRATIONS_DIR := ./app/db/migrations/versions
ENVIRONMENTS := prod dev test

validate-env:  # arguments: env(str=prod|dev|test);
	echo "${ENVIRONMENTS}" | rg -w --quiet "${env}"; \
	if [ $$? -ne 0 ]; \
	then \
		echo; \
		echo "┌────────────────────────────────────"; \
		echo "| Validation error:"; \
		echo "| Environment must be one of [${ENVIRONMENTS}], actual=${env}"; \
		echo "└────────────────────────────────────"; \
		echo; \
		exit 1; \
	fi

dc:  # arguments: env(str=prod|dev|test);
	make validate-env env="${env}"
	${DC} -f "${DC}.${env}.yaml" --project-name "${PROJECT_NAME}_${env}" up
dc-down:  # arguments: env(str=prod|dev|test);
	make validate-env env="${env}"
	${DC} -f "${DC}.${env}.yaml" --project-name "${PROJECT_NAME}_${env}" down -v --rmi local
prod:
	make dc env=prod
prod-down:
	make dc-down env=prod
dev:
	make dc env=dev
dev-down:
	make dc-down env=dev
test:
	make dc env="test" args="--abort-on-container-exit --exit-code-from test"
test-down:
	make dc-down env=test

lint:
	./scripts/lint.sh
local-test:
	./scripts/full_test.sh

rm-mypy-cache:
	rm -rf .mypy_cache/

clean:
	make prod-down
	make dev-down
	make test-down
	make rm-mypy-cache

migration:  # arguments: message(str);
	alembic revision --autogenerate -m ${message}

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade base

rm-migrations:
	rm ${MIGRATIONS_DIR}/*.py

dangerous-remigrate:
	make downgrade
	@echo "┌────────────────────────────────────┐"
	@echo "│ DB has been cleared                │"
	@echo "└────────────────────────────────────┘"
	make rm-migrations
	@echo "┌────────────────────────────────────┐"
	@echo "│ Old migrations have been deleted   │"
	@echo "└────────────────────────────────────┘"
	make migration message="init"
	@echo "┌────────────────────────────────────┐"
	@echo "│ Init migration has been made       │"
	@echo "└────────────────────────────────────┘"
	./scripts/add_enums_drop_to_migration.sh
	@echo "┌────────────────────────────────────┐"
	@echo "│ Enums drop have been fixed         │"
	@echo "└────────────────────────────────────┘"
	make migrate
	@echo "┌────────────────────────────────────┐"
	@echo "│ Migration has been migrated        │"
	@echo "└────────────────────────────────────┘"
