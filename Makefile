IOGT_TEST_PARALLEL ?= 1

# Build the project
build:
	docker-compose build
down:
	docker-compose down
makemigrations:
	docker-compose run django python manage.py makemigrations
migrate:
	docker-compose run django python manage.py migrate
setup:
	make migrate
	make update_elasticsearch_index
up:
	docker-compose up
update_elasticsearch_index:
	docker-compose run django python manage.py update_index
compile-requirements:
	docker-compose -f docker-compose.builder.yml run --rm builder
test:
	docker-compose -f docker-compose.test.yml up --build -d
	docker-compose -f docker-compose.test.yml exec -T django python manage.py collectstatic --noinput
	docker-compose -f docker-compose.test.yml exec -T django python manage.py test --noinput --parallel $(IOGT_TEST_PARALLEL)
	docker-compose -f docker-compose.test.yml down --remove-orphans
selenium-test: selenium-up selenium-local selenium-down
selenium-up:
	docker-compose -f docker-compose.selenium.yml up --build -d --scale chrome=$(IOGT_TEST_PARALLEL)
	docker-compose -f docker-compose.selenium.yml exec -T django python manage.py collectstatic --noinput
selenium-local:
	docker-compose -f docker-compose.selenium.yml exec -T django python manage.py test selenium_tests --parallel $(IOGT_TEST_PARALLEL)
selenium-down:
	docker-compose -f docker-compose.selenium.yml down --remove-orphans
