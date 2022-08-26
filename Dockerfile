ARG PROJECT_NAME=my_vocab_backend
ARG USER=${PROJECT_NAME}_user
ARG WORKDIR=/home/${USER}/${PROJECT_NAME}


FROM python:3.10-slim as base

ARG PROJECT_NAME
ARG USER
ARG WORKDIR

RUN useradd -m ${USER}
RUN pip install --upgrade pip

USER ${USER}
RUN mkdir ${WORKDIR}
WORKDIR ${WORKDIR}

ENV PATH=/home/${USER}/.local/bin:${PATH}
ENV PYTHONPATH=${WORKDIR}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIPENV_VENV_IN_PROJECT=1

COPY --chown=${USER} Pipfile Pipfile.lock ./
RUN pip install -U pipenv
RUN pipenv install --deploy


FROM base as main

ARG USER

COPY --chown=${USER} . .

CMD ["pipenv", "run", "python", "app/__main__.py"]


FROM base as pre-test

RUN pipenv install --dev --deploy


FROM pre-test as test

ARG USER

COPY --chown=${USER} . .

CMD ["pipenv", "run", "bash", "./scripts/full_test.sh"]