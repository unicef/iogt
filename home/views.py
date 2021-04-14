from django.http import HttpRequest, JsonResponse
from wagtail.core.models import Page
from .models import Section
import psycopg2
import psycopg2.extras


def migrate(request: HttpRequest) -> JsonResponse:
    homepage: Page = Page.objects.get(id=3)

    sections = get_sections_from_molo_db()

    for section in sections:
        section_page = Section(
            slug=section['slug'],
            title=section['title']
        )

        homepage.add_child(instance=section_page)

        section_page.save_revision().publish()

        homepage.save()

    msg = {'msg': 'Successfully added ' + str(len(sections)) + ' sections', 'sections': sections}
    return JsonResponse(msg, json_dumps_params={'indent': 4})


def get_sections_from_molo_by_owner(owner_id):
    # Connect to your postgres DB
    conn = psycopg2.connect("dbname=kenya user=michael")

    # Open a cursor to perform database operations
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute a query
    cur.execute("select * from wagtailcore_page where owner_id = %s", [owner_id])

    # Retrieve query results
    records = cur.fetchall()
    record_dicts = []
    for row in records:
        section = dict(row)
        record_dicts.append(section)
    return record_dicts

def get_sections_from_molo_db():
    # Connect to your postgres DB
    conn = psycopg2.connect("dbname=kenya user=michael")

    # Open a cursor to perform database operations
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Execute a query
    cur.execute("select * from wagtailcore_page where url_path ~ %s limit 300;", ['^\/home\/sections\/[^\/]*\/$'])

    # Retrieve query results
    records = cur.fetchall()
    record_dicts = []
    for row in records:
        section = dict(row)
        record_dicts.append(section)
    return record_dicts
