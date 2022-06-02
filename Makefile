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
# SSH into the django container
ssh:
	docker-compose run django /bin/bash
up:
	docker-compose up
update_elasticsearch_index:
	docker-compose run django python manage.py update_index
test:
	docker-compose -f docker-compose.test.yml up --build -d django
	docker-compose exec -T django python manage.py collectstatic --noinput
	docker-compose exec -T django coverage run --source='.' manage.py test --noinput
	docker-compose exec -T django coverage html
	docker-compose -f docker-compose.test.yml down --remove-orphans
cypress:
	docker-compose -f docker-compose.cypress.yml up --build -d django
	docker-compose exec -T django python manage.py clear_svg_to_png_map
	docker-compose exec -T django python manage.py collectstatic --noinput
selenium-test: selenium-up selenium-local selenium-down
selenium-up:
	docker-compose -f docker-compose.selenium.yml up --build -d
	docker-compose exec -T django python manage.py collectstatic --noinput
selenium-local:
	docker-compose exec -T django python manage.py test selenium_tests/basic_tests
selenium-down:
	docker-compose -f docker-compose.selenium.yml down --remove-orphans
