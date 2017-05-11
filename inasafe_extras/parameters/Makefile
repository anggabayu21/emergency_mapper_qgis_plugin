PROJECT_NAME = PARAMETERS
BUILD_DIRECTORY = ../build_$(PROJECT_NAME)

# Run pep8 style checking
#http://pypi.python.org/pypi/pep8
pep8:
	@echo
	@echo "-----------"
	@echo "PEP8 issues"
	@echo "-----------"
	@pep8 --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128,E402 . || true

# Run entire test suite
test_suite:
	@echo
	@echo "---------------------"
	@echo "Regression Test Suite"
	@echo "---------------------"
	@export PYTHONPATH=`pwd`:$(PYTHONPATH);nosetests -v --with-id --with-coverage --cover-package=. 3>&1 1>&2 2>&3 3>&- || true

# zip
package:
	@echo
	@echo "---------------------"
	@echo "Creating a package for $(PROJECT_NAME) project"
	@echo "---------------------"
	rm -rf $(BUILD_DIRECTORY)
	cp -rf . $(BUILD_DIRECTORY)
	@echo "Remove pyc files"
	find $(BUILD_DIRECTORY) -name "*.pyc" -exec rm -rf {} \;
	@echo "Remove test directories"
	find $(BUILD_DIRECTORY) -name "test" -type d -prune -exec rm -rf '{}' '+'
	@echo "Remove dot files"
	find $(BUILD_DIRECTORY) -name ".*" -prune -exec rm -rf '{}' '+'
	@echo "Remove Makefile"
	find $(BUILD_DIRECTORY) -name "Makefile" -prune -exec rm '{}' '+'
