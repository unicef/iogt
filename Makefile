up:
	docker-compose up
down:
	docker-compose down
# SSH into the django container
ssh:
	docker exec -it iogt-dg01 /bin/bash
# Build the project
build:
	docker-compose build