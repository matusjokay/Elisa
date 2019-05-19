from django.http.response import HttpResponseBadRequest

"""
HttpsMiddleware checks usage of HTTPS using is_secure from request. This check is neccessary for
secure usage of JWT authentication.
"""


class HttpsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.is_secure:
            response = self.get_response(request)
            return response
        else:
            return HttpResponseBadRequest("Only HTTPS is allowed.")
