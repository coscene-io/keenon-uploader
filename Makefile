# Makefile for python code
#
# > make help
#
# The following commands can be used.
#
# init:  sets up environment and installs requirements
# install:  Installs development requirments
# format:  Formats the code with autopep8
# lint:  Runs flake8 on src, exit if critical rules are broken
# clean:  Remove build and cache files
# env:  Source venv and environment files for testing
# leave:  Cleanup and deactivate venv
# test:  Run pytest
# run:  Executes the logic

# define the name of the virtual environment directory
VENV := .venv

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate:
	pip install virtualenv
	virtualenv -p `which python2` .venv
	$(VENV)/bin/pip install -U pip==20.3.4
	# Used for packaging, linting and testing
	$(VENV)/bin/pip install setuptools wheel flake8 pytest
	$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

.PHONY: help
help:
	@echo 'The following commands can be used.'
	@echo ''
	$(call find.functions)

.PHONY: install ## sets up environment and installs requirements
install: requirements.txt venv
	$(VENV)/bin/pip install -r requirements.txt

.PHONY: lint ## Runs flake8 on src, exit if critical rules are broken
lint: venv
	# stop the build if there are Python syntax errors or undefined names
	$(VENV)/bin/flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	$(VENV)/bin/flake8 src --count --exit-zero --statistics

.PHONY: test ## Run pytest
test: init
	$(VENV)/bin/pytest . -p no:logging -p no:warnings

SOURCE:=$(shell find cos -type f)
FULL_NAME:=$(shell python setup.py --fullname)
WHEEL_DIR=ansible/files/wheels
DIST_WHEEL=$(WHEEL_DIR)/$(FULL_NAME)-py2-none-any.whl

ansible/files/pip:
	$(VENV)/bin/pip download --platform=manylinux1_x86_64 --no-deps -d ansible/files/pip -r requirements-pip.txt

$(DIST_WHEEL): $(SOURCE) $(VENV)/bin/activate
	$(VENV)/bin/python setup.py bdist_wheel --plat-name=any
	mkdir -p $(WHEEL_DIR)
	mv dist/*.whl $(WHEEL_DIR)

$(WHEEL_DIR)/downloaded: $(DIST_WHEEL) ansible/files/pip requirements.txt
	$(VENV)/bin/pip wheel -r requirements.txt -w $(WHEEL_DIR)
	$(VENV)/bin/pip download --no-binary :all: scandir~=1.10.0 -d $(WHEEL_DIR)
	cp requirements*.txt ansible/files/
	touch $(WHEEL_DIR)/downloaded

.PHONY: build
build: $(WHEEL_DIR)/downloaded


.PHONY: build-in-docker
build-in-docker:
	docker build -t nuitka -f Dockerfile.build .
	docker run -itv $(pwd):/app nuitka --standalone --follow-imports --onefile --show-memory --show-progress --output-dir=out main.py --output-filename=cos


.PHONY: ansible
ansible: build
	ansible-playbook -i ansible/hosts.yaml ansible/site.yaml

.PHONY: clean ## Remove build and cache files
clean:
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist
	rm -rf .pytest_cache
	# Remove all pycache
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	# Remove all wheels
	rm -rf $(WHEEL_DIR)
	rm -rf ansible/files/pip
	rm -rf ansible/files/requirements*.txt
