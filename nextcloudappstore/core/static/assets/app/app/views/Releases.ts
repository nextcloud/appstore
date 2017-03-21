import {createAccordion} from '../../components/Accordion';
import {queryAll, ready} from '../../dom/Facades';

ready(() => {
    queryAll('.accordion-item').forEach(createAccordion);
});
