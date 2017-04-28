import {queryOrThrow} from '../dom/Facades';

export function createAccordion(elem: HTMLElement) {
    const title = queryOrThrow('.accordion-title', HTMLElement, elem);
    title.addEventListener('click', () => {
        elem.classList.toggle('open');
    });
}
