FROM python:3.8.1-slim-buster AS builder
ENV PIP_NO_CACHE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update --yes --quiet \
 && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    gettext \
    git \
    libpango1.0-0 \
    libpq-dev \
    libpq5 \
 && pip install --upgrade pip \
 && pip install pip-tools \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /iogt
RUN python -m venv venv
ENV PATH="/iogt/venv/bin:$PATH"
RUN pip install --upgrade pip
ARG requirements=requirements.txt
COPY ${requirements} .
RUN pip install -r $requirements

FROM python:3.8.1-slim-buster AS base
EXPOSE 8000
ENV PATH="/opt/venv/bin:$PATH" \
    PIP_NO_CACHE=1 \
    PYTHONUNBUFFERED=1
RUN useradd wagtail
RUN apt-get update --yes --quiet \
 && apt-get install --yes --quiet --no-install-recommends \
    gettext \
    libpango1.0-0 \
    libpq5 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN chown wagtail:wagtail /app

FROM base AS dev
RUN apt-get update --yes --quiet \
 && apt-get install --yes --quiet --no-install-recommends \
    tini \
 && rm -rf /var/lib/apt/lists/*
COPY --from=builder --chown=wagtail:wagtail /iogt/venv /opt/venv
COPY --chown=wagtail:wagtail . .
USER wagtail
ENTRYPOINT ["tini", "--"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS prod
# PORT variable is used by Gunicorn. Should match "EXPOSE" command.
ENV PORT=8000
USER wagtail
COPY --from=builder --chown=wagtail:wagtail /iogt/venv /opt/venv
RUN pip install "gunicorn==20.0.4"
COPY --chown=wagtail:wagtail . .
RUN python manage.py collectstatic --noinput --clear
RUN python manage.py compilemessages
CMD gunicorn iogt.wsgi:application
