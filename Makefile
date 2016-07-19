NAME = ukpds/data-driven
VERSION=0.1.$(GO_PIPELINE_COUNTER)

build:
	docker-compose build

run:
	docker-compose up -d

rebuild:
	docker-compose down
	docker-compose up -d

test:
	docker-compose run web rake spec
	docker-compose down