from django.apps import AppConfig

class AdmissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admissions"
    verbose_name = "Admissions"

    def ready(self):
        # Import signals if you later add them.
        from . import signals  # noqa
