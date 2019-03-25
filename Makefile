VERSION?=`git rev-parse --short HEAD`
DOCKER_IMAGE=unicef/molo-iogt:0.1.0
RUN_OPTIONS?=
MOLO_VERSION?=6
IOGT_VERSION?=a6e3f08

help:
	echo "help"

build:
	docker build \
			--build-arg MOLO_VERSION=${MOLO_VERSION} \
			--build-arg IOGT_VERSION=${IOGT_VERSION} \
			-t ${DOCKER_IMAGE} \
			-f Dockerfile .

.run:
	docker run \
		--rm \
		-p 8000:8000 \
		-e BROKER_URL=${BROKER_URL} \
		-e DATABASE_URL=${DATABASE_URL} \
		-e CELERY_BEAT=${CELERY_BEAT} \
		-e CELERY_WORKER=${CELERY_WORKER} \
		-e AZURE_ACCOUNT_NAME= \
		-e AZURE_ACCOUNT_KEY= \
		-e AZURE_CONTAINER= \
		${RUN_OPTIONS} \
		${DOCKER_IMAGE} \
		${CMD}

run:
	$(MAKE) .run

test:
	RUN_OPTIONS="-it" CMD="/usr/local/bin/django-admin check --deploy --verbosity 2" $(MAKE) .run

shell:
	RUN_OPTIONS="-it --entrypoint=/bin/bash" $(MAKE) .run


release:
	@echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
	docker push ${DOCKER_IMAGE}

