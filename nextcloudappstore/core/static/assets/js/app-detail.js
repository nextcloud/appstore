
class ImageSlider {

    constructor(element, autoscroll_interval, nextBtnElement,
            prevBtnElement) {
        this.element = element;
        this.strip =
            new ImageStrip(this, this.element.querySelector('.img-strip'));
        this.curSlide = 0;

        this.setSlide(this.curSlide);

        let slider = this;

        this.autoScroll = setInterval(function(){slider.increment(1)},
            autoscroll_interval);

        nextBtnElement.addEventListener('click', function() {
            slider.increment(1);
            clearInterval(slider.autoScroll);
        });
        prevBtnElement.addEventListener('click', function() {
            slider.increment(-1);
            clearInterval(slider.autoScroll);
        });
    }

    setSlide(slide) {
        let imgSpacing = 4;
        let imgWidth = this.element.offsetWidth + imgSpacing;
        this.strip.setPosX(imgWidth * slide);
        this.curSlide = slide;
    }

    increment(steps) {
        let imgCount = this.strip.images.length;
        let next = this.curSlide + steps;
        next = ((next%imgCount)+imgCount)%imgCount; // because a simple % does it wrong
        this.setSlide(next);
    }
}


class ImageStrip {

    constructor(slider, element) {
        this.slider = slider;
        this.element = element;
        this.images = findImages(this.element);

        function findImages(element) {
            let imgElements = Array.from(element.querySelectorAll('.img'));
            return imgElements.map(function(img) {
                return new Image(img);
            });
        }
    }

    setPosX(posX) {
        this.element.style.right = posX+'px';
    }
}


class Image {

    constructor(element) {
        this.element = element;
        this.element.style.backgroundImage =
            'url('+this.element.getAttribute('data-url')+')';
    }
}


(function (global) {
    'use strict';
    const AUTOSCROLL_INTERVAL = 8000;  // ms
    let document = global.document;
    let md = global.markdownit();
    let nextButton = document.querySelector('.img-slider-controls .next');
    let prevButton = document.querySelector('.img-slider-controls .prev');
    let imgSliderElement = document.getElementById('img-slider');

    let imgSlider = new ImageSlider(imgSliderElement, AUTOSCROLL_INTERVAL,
            nextButton, prevButton);

    let markdown = Array.from(document.querySelectorAll('.markdown'));
    markdown.forEach(elem => elem.innerHTML = md.render(elem.innerHTML));
}(this));
