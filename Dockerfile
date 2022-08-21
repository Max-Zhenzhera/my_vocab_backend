ARG PROJECT_NAME=my_vocab_backend
ARG GROUP=${PROJECT_NAME}_group
ARG USER=${PROJECT_NAME}_user
ARG WORKDIR=/${PROJECT_NAME}


FROM python:3.10-slim as base

ARG GROUP
ARG USER
ARG WORKDIR

WORKDIR ${WORKDIR}

ENV PYTHONPATH=${WORKDIR}
ENV PYTHONDONTWRITEBYTECODE=1

COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy


FROM base as main

ARG GROUP
ARG USER
ARG WORKDIR

COPY . .

RUN groupadd --system ${GROUP}
RUN useradd --no-create-home --group ${GROUP} ${USER}
RUN chown -R ${USER}:${GROUP} ${WORKDIR}

USER ${USER}

CMD ["python", "app/__main__.py"]


FROM base as pre-test

RUN pipenv install --dev --system --deploy


FROM pre-test as test

ARG GROUP
ARG USER
ARG WORKDIR

COPY . .

RUN groupadd --system ${GROUP}
RUN useradd --no-create-home --group ${GROUP} ${USER}
RUN chown -R ${USER}:${GROUP} ${WORKDIR}

USER ${USER}

CMD ["pytest"]