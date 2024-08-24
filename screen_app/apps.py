from django.apps import AppConfig

class ScreenAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "screen_app"

    def ready(self):
        import screen_app.templatetags.custom_filters