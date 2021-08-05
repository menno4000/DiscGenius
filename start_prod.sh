#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $SCRIPT_DIR

echo "dropping old image to force a clean rebuild with the right name"
echo "----------------------------------------"
docker image rm discgenius_api
echo ""

echo "starting services"
echo "----------------------------------------"
docker-compose -f ./docker-compose.prod.yml --env-file ./.env.prod up --build --detach