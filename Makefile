# Constants ---------------------------------------------------------------------------------------
TEST_PROJECT_NAME := my_vocab_backend_test
TEST_DC_CONFIG_FILENAME := docker-compose.test.yaml
# -------------------------------------------------------------------------------------------------

# Shortcuts ---------------------------------------------------------------------------------------
DC := docker compose
# -------------------------------------------------------------------------------------------------

# invoke scripts ----------------------------------------------------------------------------------
log-dirs:
	python ./scripts/make_directories_for_logs.py
# -------------------------------------------------------------------------------------------------

# docker compose for deployment -------------------------------------------------------------------
up:
	${DC} up

down:
	${DC} down -v --rmi local

start:
	${DC} start

stop:
	${DC} stop
# -------------------------------------------------------------------------------------------------

# docker compose for testing ----------------------------------------------------------------------
test:
	${DC} -f ${TEST_DC_CONFIG_FILENAME} --project-name ${TEST_PROJECT_NAME} up --abort-on-container-exit

down-test:
	${DC} --project-name ${TEST_PROJECT_NAME} down --rmi local
# -------------------------------------------------------------------------------------------------

# docker compose common ---------------------------------------------------------------------------
clean:
	make down
	make down-test
# -------------------------------------------------------------------------------------------------
