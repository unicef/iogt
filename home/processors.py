def show_welcome_banner(request):
    return {
        "first_time_user": request.session.get("first_time_user", True)
    }
