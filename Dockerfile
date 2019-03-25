ARG MOLO_VERSION=6
ARG IOGT_VERSION=a6e3f08
FROM praekeltfoundation/molo-bootstrap:${MOLO_VERSION}

ENV PYTHONPATH "/app"
ENV DJANGO_SETTINGS_MODULE=unicef.settings
ENV CELERY_APP=iogt

RUN apt-get update && apt-get install -y git bash
RUN git clone --depth 1 --single-branch https://github.com/praekeltfoundation/molo-iogt /app/iogt \
    && cd /app/iogt \
    && git checkout ${IOGT_VERSION} \
    && pip install -e .

ADD ./src /app

RUN LANGUAGE_CODE=en SECRET_KEY=compilemessages-key django-admin compilemessages
RUN SECRET_KEY=collectstatic-key django-admin collectstatic --noinput
RUN SECRET_KEY=compress-key django-admin compress

CMD ["iogt.wsgi:application", "--timeout", "1800"]
