export class Accordion {
    private title: HTMLElement;

    constructor(private elem: HTMLElement) {
        const title = elem.querySelector('.accordion-title') as HTMLElement;
        if (title === null) {
            throw new Error(`No content or title found for elem ${elem}`);
        }
        this.title = title;
    }

    public attachEventListeners() {
        this.title.addEventListener('click', () => {
            this.elem.classList.toggle('open');
        });
    }

}
