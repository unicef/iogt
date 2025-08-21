celery -A iogt beat --loglevel=INFO --logfile=/app/beat.log --detach
celery -A iogt worker --loglevel=INFO --logfile=/app/worker.log --detach
gunicorn iogt.wsgi:application
