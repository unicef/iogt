# core/auth_signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def mark_auth_method(sender, request, user, **kwargs):
    """
    Mark the session with how the user authenticated, based on the backend path.
    Adjust the checks to match your actual backend(s).
    """
    backend = (request.session.get('_auth_user_backend') or '').lower()

    # Heuristics – tweak strings to match your project:
    # Example matches:
    #   - allauth.account.auth_backends.AuthenticationBackend -> "local"
    #   - your.azure.b2c.backend.AzureADBackend              -> "b2c"
    if 'azure' in backend or 'b2c' in backend:
        request.session['auth_via'] = 'b2c'
    else:
        request.session['auth_via'] = 'local'
