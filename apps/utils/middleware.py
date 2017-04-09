from django.contrib.sessions.middleware import SessionMiddleware as DjangoSessionMiddleware


class SessionMiddleware(DjangoSessionMiddleware):

    def process_request(self, request):
        super().process_request(request)
        if not request.session.session_key:
            request.session.save()
            request.session.modified = True
