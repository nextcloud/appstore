export enum HttpMethod {
    DELETE = 'DELETE',
    GET = 'GET',
    PATCH = 'PATCH',
    POST = 'POST',
    PUT = 'PUT',
}

export interface IRequestData {
    url: string;
    method?: HttpMethod;
    data: object;
}

/**
 * Similar to authApiRequest but does not hit the API (/api) and therefore
 * identifies itself using a session cookie instead of a request token
 */
export function pageRequest<T>(request: IRequestData,
                               csrfToken?: string): Promise<T> {
    const method = request.method || 'GET';

    const headers = new Headers({
        'Content-Type': 'application/json',
    });

    if (csrfToken) {
        headers.append('X-CSRFToken', csrfToken);
    }

    let body: string | undefined = JSON.stringify(request.data);
    if (method === 'GET') {
        body = undefined;
    }

    const req = new Request(request.url, {
        body,
        credentials: 'include',
        headers,
        method,
    });

    return fetch(req).then((response) => convertResponse<T>(response));
}

/**
 * Performs an authenticated API request
 * @param request
 * @param csrfToken
 * @returns
 */
export function apiRequest<T>(request: IRequestData,
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

export interface ITokenData {
    token: string;
}

/**
 * Fetches the API token by providing the JSON token
 * @param csrfToken
 * @returns the API token
 */
export function fetchToken(csrfToken: string): Promise<string> {
    return pageRequest<ITokenData>({
        data: {},
        method: HttpMethod.POST,
        url: '/api/v1/token',
    }, csrfToken).then((response: ITokenData) => response.token);
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
            // sometimes a content type is set which is not expected to be
            // parsed. In that case just log a warning
            const msg = `Can only deal with JSON but received: ${contentType}`;
            console.warn(msg);
            return Promise.resolve.bind(Promise);
        }
    }
    return response.json()
        .then(Promise.reject.bind(Promise));
}
