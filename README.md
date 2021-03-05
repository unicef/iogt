# IoGT

Internet of Good Things ([IoGT][2]) is developed as a public good under a [BSD-2][3] open-source licence.

The development uses the Python programming language, building on the [Django][4] server-side web framework combined with the [Wagtail][5] content management system.

In line with the latest Wagtail [Long Term Support release][6], IoGT 2.x supports:
- Wagtail 2.11.x
- Django 2.2.x, 3.0.x and 3.1.x
- Python 3.6, 3.7, 3.8 and 3.9
- PostgreSQL, MySQL and SQLite as database backends

## Getting started

If you'd like to contribute to IoGT development, the best way to get started is to clone a copy of this repository and run the code on your machine.
```
git clone https://github.com/unicef/iogt.git
cd iogt
```

Create an [isolated Python environment][1], into which we will install the project's dependencies. This is highly recommended so that the requirements of this project don't interfere with any other Python environments you may have in your system, including the global Python environment. We also recommend that you create a new environment outside of the project directory. 
```
python3 -m venv <path_to_venv_dir>
source <path_to_venv_dir>/bin/activate
pip install -r requirements.txt
```

Create the database. By default, an SQLite database will be created.
```
./manage.py migrate
```

Create a super user account for administration purposes.
```
./manage.py createsuperuser
```

Finally, start the server.
```
./manage.py runserver
```

Once running, navigate to http://localhost:8000 in your browser.


[1]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
[2]: https://www.unicef.org/innovation/IoGT
[3]: https://github.com/unicef/iogt/blob/develop/LICENSE
[4]: https://www.djangoproject.com/
[5]: https://wagtail.io/
[6]: https://github.com/wagtail/wagtail/wiki/Release-schedule
