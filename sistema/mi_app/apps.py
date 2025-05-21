from django.apps import AppConfig


class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mi_app'
    
    def ready(self):
        import mi_app.signals