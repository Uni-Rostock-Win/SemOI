from django.apps import AppConfig


class PagesConfig(AppConfig):

    name = "pages"
    verbose_name = "main page module"

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)

    def ready(self):
        print("app ready")
