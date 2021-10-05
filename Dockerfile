# Image with prepared python environment
FROM python:3.9.7-slim as base


WORKDIR /my_vocab_backend

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --system --deploy

ENV PYTHONPATH=/my_vocab_backend



# Image with ready to run production
FROM base as main


COPY . .

RUN python ./scripts/prepare.py

CMD ["python", "app/main.py"]



# Image with prepared python testing environment
FROM base as pre-test


RUN pip install pytest pytest-asyncio



# Image with ready to run tests
FROM pre-test as test


COPY . .

RUN python ./scripts/prepare.py

CMD ["pytest"]