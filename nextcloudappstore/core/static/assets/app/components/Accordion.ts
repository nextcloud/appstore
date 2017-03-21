import {queryOrThrow} from '../dom/Facades';

export function createAccordion(elem: HTMLElement) {
    const title = queryOrThrow<HTMLElement>('.accordion-title', elem);
    title.addEventListener('click', () => {
        elem.classList.toggle('open');
    });
}
