import {Accordion} from '../../components/Accordion';
import {queryAll, ready} from '../../dom/Facades';

ready(() => {
    queryAll('.accordion-item').forEach((elem) => {
        const accordion = new Accordion(elem as HTMLElement);
        accordion.attachEventListeners();
    });
});
