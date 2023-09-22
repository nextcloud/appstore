from functools import wraps

from django.core.cache import caches
from django.http.response import HttpResponse
from django.utils.cache import get_conditional_response
from django.utils.http import quote_etag


def etag_redis(etag_func):
    return condition_redis(etag_func)


def condition_redis(etag_func):
    """Cache of reply for HTTP request in Redis, where Redis Key is the ETag of reply.

    .. note:: It is the dev version, and can be used only for the one endpoint
        if all goes well it will be modified to support multiply endpoints.
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            # The value from etag_func() could be quoted or unquoted.
            res_etag = etag_func(request, *args, **kwargs) if etag_func else None
            res_etag = quote_etag(res_etag) if res_etag is not None else None

            response = get_conditional_response(
                request,
                etag=res_etag,
            )
            if response is None:
                cache = caches["default"]
                cached_response = cache.get(res_etag)
                if not cached_response:
                    response = func(request, *args, **kwargs)
                    if response.status_code == 200:
                        cache.set(res_etag, response.rendered_content, 10 * 60)
                else:
                    response = HttpResponse(content=cached_response, content_type="application/json")
            if request.method in ("GET", "HEAD"):
                if res_etag:
                    response.headers.setdefault("ETag", res_etag)
            return response

        return inner

    return decorator
