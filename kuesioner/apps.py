from django.apps import AppConfig


class KuesionerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kuesioner'

    def ready(self):
        import kuesioner.signals