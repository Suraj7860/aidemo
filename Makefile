# Documentation
PACKAGE=$(REPO)/$(PACKAGE_DIR)
APIDOC_OPTIONS = -d 1 --no-toc --separate --force --private

.PHONY: doc test coverage notebook


# PRODUCTION COMMANDS
deploy: distclean package install
	source conf/app-profile.sh &&\
	twine upload -r psa $$BIN/dist/*
	# twine upload --repository-url http://repository.inetpsa.com/api/pypi/pypi-virtual $$BIN/dist/*

package: install
	# @echo Building $(current_dir)...
	source conf/app-profile.sh && \
	cd $$BIN/ &&\
	python setup.py sdist

train: install
	source conf/app-profile.sh &&\
	python $$BIN/diaman/pipeline/cli.py /user/u542310/gmt00/gmt00-diaman-ai/data/standard default

doccano_input: install
	source conf/app-profile.sh &&\
	python $$BIN/diaman/pipeline/doccano_labelling.py ${PARAMS}

enrich_dict: install
	source conf/app-profile.sh &&\
	python $$BIN/diaman/pipeline/enrich_word_dict.py ${PARAMS}


# CLEANING COMMANDS
clean:
	@echo Cleaning $(current_dir)...
	find . -name __pycache__ -print | xargs rm -rf 2>/dev/null
	find . -name '*.pyc' -delete
	rm -rf .pytest_cache/
	rm -rf install
	rm -rf .install_jupyter

distclean: clean
	source conf/app-profile.sh && \
	rm -rf $$BIN/dist
	rm -rf $$BIN/build
	find . -name '*.egg-info' -exec rm -rf {} +


# INSTALLATION COMMANDS
rename:
	sh ./script/change_name.sh

.venv3:
	rm install || true &&\
	/soft/python3/bin/virtualenv ./.venv3 &&\
	source conf/app-profile.sh &&\
	pip install $$PIP_OPTIONS --upgrade pip pypandoc

install: .venv3 bin/setup.py
	source conf/app-profile.sh &&\
	pip install $$PIP_OPTIONS --upgrade pip pypandoc &&\
	cd $$BIN/ &&\
	pip install $$PIP_OPTIONS -e .[dev] &&\
	touch install

.install_jupyter: install
	source conf/app-profile.sh &&\
	pip install $$PIP_OPTIONS jupyter &&\
	jupyter nbextension enable --py --sys-prefix widgetsnbextension &&\
	touch .install_jupyter

notebook:  .install_jupyter
	source conf/app-profile.sh && \
	./script/notebook.sh start


# DEVELOPMENT COMMANDS
test: install
	source conf/app-profile.sh &&\
	cd $$BIN/ &&\
	pip install $$PIP_OPTIONS -e .[tests] &&\
	coverage run --branch --source diaman/domain/ -m pytest &&\
	coverage report -m

doc:
	source conf/app-profile.sh &&\
	rm doc/source/generated/*  || true
	rm -r doc/build/html/* || true
	export PYTHONPATH=$$(pwd):$$PYTHONPATH &&\
	sphinx-apidoc $(APIDOC_OPTIONS) -o doc/source/generated/ $(PACKAGE) &&\
	sphinx-build -M html doc/source doc/build

describe:
	sh ./script/describe.sh
