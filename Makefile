# app defaults
app=bank_admin
port=8002
browsersync_port=3002
browsersync_ui_port=3032

NODE_MODULES := node_modules
MTP_COMMON := $(NODE_MODULES)/money-to-prisoners-common

ifeq ($(VIRTUAL_ENV),)
	PYTHON_BIN=$(shell if [ -d "venv" ]; then echo "venv/bin/"; fi)
else
	PYTHON_BIN=$(VIRTUAL_ENV)/bin/
endif

# include shared Makefile, installing it if necessary
.PHONY: install-common
install-common:
	@echo "The installation process is about to start. It usually takes a while."
	@echo "The only thing that this script doesn't do is set up the API. While"
	@echo "installation is running, head to https://github.com/ministryofjustice/money-to-prisoners-api"
	@echo "to find out how to run it."
	@$(PYTHON_BIN)pip install money-to-prisoners-common
	@$(eval export PYTHON_LIBS=$(shell $(PYTHON_BIN)python find_common.py))

$(NODE_MODULES):
	@npm install
	@npm install `cat $(PYTHON_LIBS)/mtp_common/npm_requirements.txt`
	@echo Copying mtp_common assets to node_modules
	@mkdir $(MTP_COMMON)
	@cp -R $(PYTHON_LIBS)/mtp_common/assets $(MTP_COMMON)

%: install-common $(NODE_MODULES)
	@$(MAKE) -f $(PYTHON_LIBS)/mtp_common/Makefile app=$(app) port=$(port) browsersync_port=$(browsersync_port) browsersync_ui_port=$(browsersync_ui_port) $@
