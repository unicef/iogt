from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache

@never_cache
def csrf_token_api(request):
    """
    Returns the current CSRF token.
    Forces Django to generate and set the `csrftoken` cookie if it doesn't exist.
    """
    return JsonResponse({'csrfToken': get_token(request)})
