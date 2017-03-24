import {queryAll} from '../dom/Facades';
import {Maybe} from '../Utils';

declare class SliderLogic {
    constructor(images: string[], start: number);
}

declare class ImageSlider {
    constructor(logic: SliderLogic, container: HTMLElement);
}

export function createSlideshow(container: HTMLElement) {
    const images = queryAll('.img', container)
        .filter((elem) => elem instanceof HTMLImageElement)
        .map((elem) => (elem as HTMLImageElement).src);

    new Maybe(images[0])
        .map((src) => {
            const img = new Image();
            img.src = src;
            return img;
        })
        .ifPresent((img) => {
            img.addEventListener('load', () => {
                const logic = new SliderLogic(images, 0);
                new ImageSlider(logic, container);
            });
        });
}
