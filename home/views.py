from django.http import HttpRequest, JsonResponse
from wagtail.core.models import Page
from .models import Section

def migrate(request: HttpRequest) -> JsonResponse:
    
    homepage: Page = Page.objects.get(id=3)

    section_name = "health"
    section_page = Section(
        slug=section_name,
        title=section_name
    )

    homepage.add_child(instance=section_page)

    section_page.save_revision().publish() 

    homepage.save()

    msg = { 'msg': 'Sucessfully added a section called ' + section_name }
    return JsonResponse(msg)
