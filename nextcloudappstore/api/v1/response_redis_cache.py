from functools import wraps

from django.core.cache import caches
from django.http.response import HttpResponse
from django.utils.cache import get_conditional_response
from django.utils.http import quote_etag


def etag_redis(etag_func, key_prefix: str):
    """Cache of reply for HTTP request in Redis, where Redis Key is the ETag of reply.

    .. note:: It is the dev version, and can be used only for the one endpoint
        if all goes well it will be modified to support multiply endpoints.
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            # The value from etag_func() could be quoted or unquoted.
            res_etag = quote_etag(etag_func(request, *args, **kwargs))

            response = get_conditional_response(
                request,
                etag=res_etag,
            )
            if response is None:
                cache = caches["default"]
                redis_key = key_prefix + res_etag.replace(" ", "_").replace('"', "")
                cached_response = cache.get(redis_key)
                if not cached_response:
                    response = func(request, *args, **kwargs)
                    if response.status_code == 200:
                        # apps.json size > 12 MB, to store 100 caches we need 1.2 GB
                        # let assume we don't get more than 100 release updates in 2.5 minutes.
                        cache.set(redis_key, response.rendered_content, 150)
                else:
                    cache.touch(redis_key, 90)
                    response = HttpResponse(content=cached_response, content_type="application/json")
            if request.method in ("GET", "HEAD"):
                response.headers.setdefault("ETag", res_etag)
            return response

        return inner

    return decorator
