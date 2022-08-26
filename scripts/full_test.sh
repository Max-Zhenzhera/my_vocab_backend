#!/bin/bash

echo "Linting..."
. ${0%/*}/lint.sh
echo "Testing..."
pytest