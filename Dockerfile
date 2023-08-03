FROM python:3.8.1-slim-buster AS base
EXPOSE 8000
ENV PIP_NO_CACHE=1 \
    PYTHONUNBUFFERED=1
RUN useradd wagtail
RUN apt-get update --yes --quiet \
 && apt-get install --yes --quiet --no-install-recommends \
    gettext \
    libpango1.0-0 \
    libpq5 \
 && pip install --upgrade pip \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN chown wagtail:wagtail /app

FROM base AS dev
COPY requirements*.txt /tmp/
RUN apt-get update --yes --quiet \
 && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    tini \
 && pip install pip-tools \
 && pip install -r /tmp/requirements.txt \
 && pip install -r /tmp/requirements.dev.txt \
 && rm -rf /var/lib/apt/lists/*
COPY --chown=wagtail:wagtail . .
USER wagtail
ENTRYPOINT ["tini", "--"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM dev AS builder
USER root
WORKDIR /iogt
RUN pip wheel --no-deps --wheel-dir wheels -r /tmp/requirements.txt

FROM base AS prod
# PORT variable is used by Gunicorn. Should match "EXPOSE" command.
ENV PORT=8000
USER root
COPY --from=builder /iogt/wheels /tmp/wheels
RUN pip install "gunicorn==20.0.4" /tmp/wheels/* \
 && rm -rf /tmp/requirements*.txt /tmp/wheels
COPY --chown=wagtail:wagtail . .
USER wagtail
RUN python manage.py collectstatic --noinput --clear
RUN python manage.py compilemessages
CMD gunicorn iogt.wsgi:application
