from html.parser import HTMLParser
import re

from django.conf import settings
from django.template.defaultfilters import urlencode
from django.urls import reverse


SAFE_EXTERNAL_LINK_PATTERNS = getattr(settings, 'SAFE_EXTERNAL_LINK_PATTERNS', ())
safe_urls = ''
if SAFE_EXTERNAL_LINK_PATTERNS:
    safe_urls = '(?!(' + '|'.join(SAFE_EXTERNAL_LINK_PATTERNS) + '))'


class RewriteExternalLinksMiddleware:
    """
    Rewrite all external links to go via a message page.
    Rewrite:
        <a href="http://www.example.com">
    To:
        <a href="/external-link/?next=http://www.example.com">
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.extlinks = re.compile(r'''
            (?P<before><a[^>]*href=['"]?)  # content from `<a` to `href='`
            (?P<link>https?://{}[^'">]*)  # href link
            (?P<after>[^>]*)  # content after href to closing bracket `>`
        '''.format(safe_urls), re.VERBOSE)

    def __call__(self, request):
        response = self.get_response(request)
        external_link_root = reverse('external-link')

        # neither external_link_root nor request.path include hostname
        if response.streaming:
            return response

        h = HTMLParser()
        html_content_type = 'text/html' in response.get('content-type', '')
        start_link = request.path.startswith(external_link_root)

        if (response.content and html_content_type and not start_link):
            next = request.path

            def linkrepl(m):
                return '{before}{root}?next={link}&from={next}{after}'.format(
                    root=external_link_root,
                    next=next,
                    before=m.group('before'),
                    # unescape the link before encoding it to ensure entities
                    # such as '&' don't get double escaped
                    link=urlencode(h.unescape(m.group('link')), safe=''),
                    after=m.group('after'),
                )
            response.content = self.extlinks.sub(
                linkrepl,
                response.content.decode('utf-8')
            )
            response['Content-Length'] = len(response.content)

        return response
