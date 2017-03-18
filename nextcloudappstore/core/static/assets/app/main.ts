const script = document.querySelector('script[data-view]');

if (script !== null && script instanceof HTMLScriptElement) {
    const viewPath = script.dataset.view as string;

    /* tslint:disable:no-var-requires */
    require([viewPath], ({main}: {main: () => void}) => {
        if (document.readyState !== 'loading') {
            main();
        } else {
            document.addEventListener('DOMContentLoaded', main);
        }

    });
} else {
    console.error('No configured view found, did you add it?');
}
