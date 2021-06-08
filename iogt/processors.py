def get_domain(request):
    return {
        "domain": request.META.get("HTTP_HOST")
    }


def get_referer(request):
    return {
        "referer": request.META.get("HTTP_REFERER")
    }
