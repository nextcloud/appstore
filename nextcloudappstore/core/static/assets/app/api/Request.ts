export const HttpMethod = {
    DELETE: 'DELETE' as 'DELETE',
    GET: 'GET' as 'GET',
    PATCH: 'PATCH' as 'PATCH',
    POST: 'POST' as 'POST',
    PUT: 'PUT' as 'PUT',
};

export type RequestData = {
    url: string;
    method?: keyof typeof HttpMethod;
    data: Object;
};

/**
 * Similar to authApiRequest but does not hit the API (/api) and therefore
 * identifies itself using a session cookie instead of a request token
 */
export function pageRequest<T>(request: RequestData,
                               csrfToken?: string): Promise<T> {
    const headers = new Headers({
        'Content-Type': 'application/json',
    });

    if (csrfToken) {
        headers.append('X-CSRFToken', csrfToken);
    }

    const req = new Request(request.url, {
        body: JSON.stringify(request.data),
        credentials: 'include',
        headers,
        method: request.method || 'GET',
    });

    return fetch(req).then((response) => convertResponse<T>(response));
}

/**
 * Performs an authenticated API request
 * @param request
 * @param csrfToken
 * @returns
 */
export function apiRequest<T>(request: RequestData,
                              csrfToken: string): Promise<T> {
    return fetchToken(csrfToken).then((token) => {
        const req = new Request(request.url, {
            body: JSON.stringify(request.data),
            headers: new Headers({
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
            }),
            method: request.method || 'GET',
        });
        return fetch(req).then((response) => convertResponse<T>(response));
    });
}

export type TokenData = {
    token: string;
};

/**
 * Fetches the API token by providing the JSON token
 * @param csrfToken
 * @returns the API token
 */
export function fetchToken(csrfToken: string): Promise<string> {
    return pageRequest<TokenData>({
        data: {},
        method: 'POST',
        url: '/api/v1/token',
    }, csrfToken).then((response: TokenData) => response.token);
}

/**
 * Handles response errors and turns the response content into either text
 * or JSON based on content type
 * @param response
 * @returns
 */
function convertResponse<T>(response: Response): Promise<T> {
    if (response.status >= 200 && response.status < 400) {
        const contentType = response.headers.get('Content-Type');
        if (contentType === 'application/json') {
            return response.json();
        } else if (contentType === null || contentType === undefined ||
            contentType === '') {
            // no content type, we don't care
            return Promise.resolve.bind(Promise);
        } else {
            const msg = `Can only deal with JSON but received: ${contentType}`;
            console.error(msg);
        }
    }
    return response.json()
        .then(Promise.reject.bind(Promise));
}
