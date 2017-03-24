import {createAccordion} from '../../components/Accordion';
import {queryAll, ready} from '../../dom/Facades';

ready.then(() => {
    queryAll('.accordion-item').forEach(createAccordion);
});
