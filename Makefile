# Auto-configure a demo openerp instance, with a specific virtualenv, postgres user and configuration file

CWD         = $(shell pwd)
VENV        = .virtualenv
PROJECT     = demo_61
CONFIGFILE  = openerp.conf

# PostgreSQL
DBHOST      = localhost
DBPORT      = 5432
DBUSER      = $(PROJECT)
DBPASS      = $(PROJECT)

# OpenERP
DBOPTIONS   = -r $(DBUSER) -w $(DBPASS) --db_host=$(DBHOST) --db_port=$(DBPORT)
ADDONS      = $(CWD)/addons,$(CWD)/web/addons

help:
	@echo "  init        Initialize the environment (calls python, postgresql and config)"
	@echo "  python      Create the python virtualenv and install needed modules inside"
	@echo "  postgresql  Create the PostgreSQL user"
	@echo "  config      Create the OpenERP config file"
	@echo "  run         Run the OpenERP service"
	@echo ""
	@echo "To initialize a test instance, run : make init && make run"
	@echo "Then, go to http://localhost:8069 on your favorite web browser"

python:
	@echo "Initialize python virtual environment"
	@virtualenv $(VENV)
	@. $(VENV)/bin/activate && pip install -r requirement.pip

postgresql:
	@echo "Create the PostgreSQL user $(DBUSER)"
	@createuser -SdRE $(DBUSER)
	@psql -c "ALTER USER $(DBUSER) ENCRYPTED PASSWORD '$(DBPASS)';" postgres

config:
	@echo "Create config file for OpenERP"
	. $(VENV)/bin/activate && ./server/openerp-server -c $(CONFIGFILE) -s --load=base $(DBOPTIONS) --addons-path=$(ADDONS) --stop-after-init

init: python postgresql config

run:
	. $(VENV)/bin/activate && ./server/openerp-server -c $(CONFIGFILE)

