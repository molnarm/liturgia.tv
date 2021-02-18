from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin


class RedirectToCustomDomainMiddleware(MiddlewareMixin):
    def process_request(self, request):
        domain = 'liturgia.tv'
        host = request.get_host()
        if (domain not in host):
            redirect_url = '%s://%s%s' % (request.scheme, domain,
                                          request.get_full_path())
            return HttpResponsePermanentRedirect(redirect_url)