#!/bin/bash

flake8 app && \
flake8 tests && \
isort -c app && \
isort -c tests && \
mypy app && \
mypy tests \
    --disable-error-code=override \
    --disable-error-code=misc \
    --disable-error-code=no-untyped-def \
    --disable-error-code=no-any-return