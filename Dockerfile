# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.8.1-slim-buster

# Add user that will be used in the container.
RUN useradd wagtail

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

COPY requirements.txt /

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet \
  && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    gettext \
    git \
    libpq5 \
    libpq-dev \
    libpango1.0-0 \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir "gunicorn==20.0.4" \
 && pip install --no-cache-dir -r /requirements.txt \
 && apt remove --yes --quiet git build-essential libpq-dev \
 && apt autoremove --yes --quiet \
 && rm -rf /var/lib/apt/lists/*

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Compile files for localization
RUN python manage.py compilemessages

# Start the application server.
CMD gunicorn iogt.wsgi:application
