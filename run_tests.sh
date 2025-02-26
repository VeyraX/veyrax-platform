#!/usr/bin/env bash

# Start Docker If Needed!
# docker-compose up -d

# Load .env variables and run tests with Python path setup
(set -a; source .env; set +a; \
 PYTHONPATH=$PYTHONPATH:./aci_server pytest aci_server/integrations/google_calendar/tests.py -v -s)
