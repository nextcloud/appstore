export class Accordion {
    private title: HTMLElement;
    private content: HTMLElement;

    constructor(private elem: HTMLElement) {
        const title = elem.querySelector('.accordion-title') as HTMLElement;
        const content = elem.querySelector('.accordion-content') as HTMLElement;
        if (title === null || content === null) {
            throw new Error(`No content or title found for elem ${elem}`);
        }
        this.title = title;
        this.content = content;
    }

    public attachEventListeners() {
        this.title.addEventListener('click', () => {
            this.elem.classList.toggle('open');
        });
    }

}
