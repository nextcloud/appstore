import { queryOrThrow } from '../dom/Facades';
export function createAccordion(elem) {
    const title = queryOrThrow('.accordion-title', HTMLElement, elem);
    title.addEventListener('click', () => {
        elem.classList.toggle('open');
    });
}
//# sourceMappingURL=Accordion.js.map