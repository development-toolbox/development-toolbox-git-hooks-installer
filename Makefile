.PHONY: test
test:
	docker-compose -f tests/docker/docker-compose.yml up --build --abort-on-container-exit
