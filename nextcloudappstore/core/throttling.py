from rest_framework.throttling import ScopedRateThrottle


class PostThrottle(ScopedRateThrottle):
    def allow_request(self, request, view):
        if request.method == 'POST':
            return super().allow_request(request, view)
        else:
            return True
