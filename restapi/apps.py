from django.apps import AppConfig


class RestapiConfig(AppConfig):
    name = 'restapi'
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        import restapi.signals
