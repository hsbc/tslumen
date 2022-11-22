## Configs and vars ###################################################
SHELL = bash
.SHELLFLAGS = -o pipefail -c

SOURCEDIR = tslumen
TESTSDIR  = tests
DOCSDIR = doc

.PHONY: doc docs tests build


## Badges #############################################################
badge_status:
	$(eval ok := `[ $(status) -eq 0 ] && echo "passing" || echo "failing"`)
	$(eval color := `[ $(status) -eq 0 ] && echo "\#50ca22" || echo "\#dc6650"`)
	python -m pybadges --left-text=$(text) --right-text=$(ok) --right-color=$(color) > $(out)

badge_style:
	$(eval ok := `[ $(score_style) -eq 0 ] && echo "black" || echo "error"`)
	$(eval color := `[ $(score_style) -eq 0 ] && echo "\#000000" || echo "\#dc6650"`)
	python -m pybadges --left-text="code style" --right-text=$(ok) --right-color=$(color) > $(out)

badge_lint:
	$(eval color := `[ $(score_lint) -eq 0 ] && echo "\#50ca22" || echo "\#a2a2a2"`)
	python -m pybadges --left-text=flake8 --right-text="$(score_lint) issues" --right-color=$(color) > $(out)

badge_mypy:
	$(eval color := `[ $(score_mypy) -eq 0 ] && echo "\#50ca22" || echo "\#a2a2a2"`)
	python -m pybadges --left-text=mypy --right-text="$(score_mypy) issues" --right-color=$(color) > $(out)

badge_coverage:
	$(eval color :=`\
[ $(score_coverage) -lt 30 ] && echo "\#dc6650" || \
[ $(score_coverage) -lt 60 ] && echo "\#f78344" || \
[ $(score_coverage) -lt 70 ] && echo "\#dbb327" || \
[ $(score_coverage) -lt 80 ] && echo "\#a6a82d" || \
[ $(score_coverage) -lt 90 ] && echo "\#9ac812" || \
echo "\#50ca22"`)
	python -m pybadges --left-text=coverage --right-text="$(score_coverage)%" --right-color="$(color)" > $(out)


## Code Quality #######################################################
style:
	black $(SOURCEDIR)
	@-black -q --check $(SOURCEDIR); make score_style=$$? out=$(DOCSDIR)/source/_static/badge_style.svg badge_style

lint:
	-flake8 $(SOURCEDIR)
	@-make score_lint=`flake8 --count $(SOURCEDIR) | tail -1` out=$(DOCSDIR)/source/_static/badge_lint.svg badge_lint

type:
	-mypy $(SOURCEDIR)
	@-make score_mypy="`mypy --no-error-summary $(SOURCEDIR) | wc -l`" out=$(DOCSDIR)/source/_static/badge_mypy.svg badge_mypy

cq:
	@-make style
	@-make lint
	@-make type


## Tests ##############################################################
test_run:
	coverage run -m pytest $(TESTSDIR)

test_coverage:
	-coverage report -m -i

tests:
	@-make test_run; make text=tests status=$$? out=$(DOCSDIR)/source/_static/badge_tests.svg badge_status
	@-make test_coverage
	@-make score_coverage=`coverage report | tail -n 1 | sed "s/.* \(.*\)%/\1/"` out=$(DOCSDIR)/source/_static/badge_coverage.svg badge_coverage


## Build ##############################################################
bdist:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	python -m build -n
	twine check dist/*

clean:
	rm -rf build dist tslumen/_version.py tslumen.egg-info

install:
	pip install -e .

build: clean
	@-make bdist;make text=build status=$$? out=$(DOCSDIR)/source/_static/badge_build.svg badge_status


## Docs ###############################################################
docsgen:
	rm -rf $(SOURCEDIR)/api/*
	sphinx-apidoc -M -f -o $(DOCSDIR)/source/api/ $(SOURCEDIR)

doc: install
	cp CHANGELOG.md $(DOCSDIR)/source
	cp CONTRIBUTING.md $(DOCSDIR)/source
	cd $(DOCSDIR)/ && make clean
	cd $(DOCSDIR)/ && make github

docs:
	@-make doc;make text=docs status=$$? out=$(DOCSDIR)/source/_static/badge_docs.svg badge_status


## All ################################################################
all:
	@-make cq
	@-make tests
	@-make build
	@-make docs
	python -m pybadges --left-text=python --right-text=">=3.6,<3.10" --right-color="#1384c5" > $(DOCSDIR)/source/_static/badge_python.svg

