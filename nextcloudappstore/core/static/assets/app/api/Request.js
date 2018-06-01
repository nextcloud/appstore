export var HttpMethod;
(function (HttpMethod) {
    HttpMethod["DELETE"] = "DELETE";
    HttpMethod["GET"] = "GET";
    HttpMethod["PATCH"] = "PATCH";
    HttpMethod["POST"] = "POST";
    HttpMethod["PUT"] = "PUT";
})(HttpMethod || (HttpMethod = {}));
export function pageRequest(request, csrfToken) {
    const method = request.method || 'GET';
    const headers = new Headers({
        'Content-Type': 'application/json',
    });
    if (csrfToken) {
        headers.append('X-CSRFToken', csrfToken);
    }
    let body = JSON.stringify(request.data);
    if (method === 'GET') {
        body = undefined;
    }
    const req = new Request(request.url, {
        body,
        credentials: 'include',
        headers,
        method,
    });
    return fetch(req).then((response) => convertResponse(response));
}
export function apiRequest(request, csrfToken) {
    return fetchToken(csrfToken).then((token) => {
        const req = new Request(request.url, {
            body: JSON.stringify(request.data),
            headers: new Headers({
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
            }),
            method: request.method || 'GET',
        });
        return fetch(req).then((response) => convertResponse(response));
    });
}
export function fetchToken(csrfToken) {
    return pageRequest({
        data: {},
        method: HttpMethod.POST,
        url: '/api/v1/token',
    }, csrfToken).then((response) => response.token);
}
function convertResponse(response) {
    if (response.status >= 200 && response.status < 400) {
        const contentType = response.headers.get('Content-Type');
        if (contentType === 'application/json') {
            return response.json();
        }
        else if (contentType === null || contentType === undefined ||
            contentType === '') {
            return Promise.resolve.bind(Promise);
        }
        else {
            const msg = `Can only deal with JSON but received: ${contentType}`;
            console.warn(msg);
            return Promise.resolve.bind(Promise);
        }
    }
    return response.json()
        .then(Promise.reject.bind(Promise));
}
//# sourceMappingURL=Request.js.map