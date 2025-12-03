from django.apps import AppConfig


class AdminLoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_login'
    
    def ready(self):
        import admin_login.auth_signals
