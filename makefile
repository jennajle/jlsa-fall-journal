include common.mk

API_DIR = server
DB_DIR = data
REQ_DIR = .

PYTESTFLAGS = -vv --verbose --cov-branch --cov-report term-missing --tb=short -W ignore::FutureWarning

FORCE:

prod: all_tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: FORCE
	cd $(API_DIR); make tests
	cd $(DB_DIR); make tests

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt
	@echo "You should set PYTHONPATH to: "
<<<<<<< HEAD
    @echo $(shell pwd)
	
=======
    	@echo $(shell pwd)

>>>>>>> 2330f9934f0a98e46972fc69775cfeee7ba8f30f
docs: FORCE
	cd $(API_DIR); make docs
