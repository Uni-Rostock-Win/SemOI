class JSONTranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.translations = {
            "en": {"greetings": "Hello", "header": "Welcome Django!"},
            "de": {"greetings": "Moin", "header": "Willkommen Django!"},
        }

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if "de" in request.META["HTTP_ACCEPT_Language"]:
            response.context_data["translation"] = self.translations
            return response
        return response
