# IoGT

Internet of Good Things ([IoGT](https://www.unicef.org/innovation/IoGT)) is developed as a public good under a [BSD-2](https://github.com/unicef/iogt/blob/develop/LICENSE) open-source licence.

The development uses the Python programming language, building on the [Django](https://www.djangoproject.com/) server-side web framework combined with the [Wagtail](https://wagtail.io/) content management system.

Inline with the latest Wagtail [Long Term Support release](https://github.com/wagtail/wagtail/wiki/Release-schedule), IoGT 2.x supports:
- Wagtail 2.11.x
- Django 2.2.x, 3.0.x and 3.1.x
- Python 3.6, 3.7, 3.8 and 3.9
- PostgreSQL, MySQL and SQLite as database backends

## Getting started

If you'd like to contribute to IoGT development, the best way to get started is to clone a copy of this repository and run the code on your machine.

A minimal set of instructions for achieving this are:

```
mkdir iogt-dev
cd iogt-dev
git clone https://github.com/unicef/iogt.git
python3 -m venv venv
source ./venv/bin/activate

cd iogt
pip install -r requirements.txt
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```
