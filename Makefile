.PHONY: test backend-test frontend-build

test: backend-test frontend-test frontend-build

backend-test:
	python -m pytest backend/tests -q

frontend-build:
	npm --prefix frontend run build

frontend-test:
	npm --prefix frontend test
