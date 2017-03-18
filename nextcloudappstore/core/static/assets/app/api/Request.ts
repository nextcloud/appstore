export type ApiRequest = {
    url: string;
    method?: string;
    data: JSON;
};

/**
 * Performs an authenticated API request
 * @param request
 * @param csrfToken
 * @returns
 */
export function apiRequest(request: ApiRequest,
                           csrfToken: string): Promise<string|JSON> {
    return fetchToken(csrfToken).then((token) => {
        const req = new Request(request.url, {
            body: JSON.stringify(request.data),
            headers: new Headers({
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
            }),
            method: request.method || 'GET',
        });
        return fetch(req).then(convertResponse);
    });
}

/**
 * Fetches the API token by providing the JSON token
 * @param csrfToken
 * @returns the API token
 */
function fetchToken(csrfToken: string): Promise<string> {
    const request = new Request('/api/v1/token', {
        credentials: 'include',
        headers: new Headers({
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        }),
        method: 'POST',
    });
    return fetch(request).then(convertResponse);
}

/**
 * Handles response errors and turns the response content into either text
 * or JSON based on content type
 * @param response
 * @returns
 */
function convertResponse(response: Response): Promise<string|JSON> {
    if (response.status >= 200 && response.status < 400) {
        if (response.headers.get('Content-Type') === 'application/json') {
            return response.json();
        } else {
            return response.text();
        }
    }
    return response.json()
        .then(Promise.reject.bind(Promise));
}
