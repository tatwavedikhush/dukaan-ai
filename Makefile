.PHONY: test backend-test frontend-test frontend-build

test:
	./scripts/test.sh

backend-test:
	python -m pytest backend/tests -q

frontend-build:
	npm --prefix frontend run build

frontend-test:
	npm --prefix frontend test
