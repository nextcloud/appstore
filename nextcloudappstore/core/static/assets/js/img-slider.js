
function ImageSlider(element, nextBtnElement, prevBtnElement) {
    this.element = element;
    this.strip =
        new ImageStrip(this, this.element.querySelector('.img-strip'));
    this.curSlide = 0;

    nextBtnElement.addEventListener('click', () => this.increment(1));
    prevBtnElement.addEventListener('click', () => this.increment(-1));
    this.setSlide(this.curSlide);
}

ImageSlider.prototype.setSlide = function(slide) {
    var imgSpacing = 4;
    var imgWidth = this.element.offsetWidth + imgSpacing;
    this.strip.setPosX(imgWidth*slide);
};

ImageSlider.prototype.increment = function(steps) {
    this.curSlide = Math.abs((this.curSlide+steps) % this.strip.images.length);
    this.setSlide(this.curSlide);
};


function ImageStrip(slider, element) {
    this.slider = slider;
    this.element = element;
    this.images = findImages(this.element);

    function findImages(element) {
        var imgElements = Array.from(element.querySelectorAll('.img'));
        return imgElements.map(function(img) {
            return new Image(img);
        });
    }
}

ImageStrip.prototype.setPosX = function(posX) {
    this.element.style.right = posX+'px';
};


function Image(element) {
    this.element = element;
    this.element.style.backgroundImage =
        'url('+this.element.getAttribute('data-url')+')';
}

(function (window) {
    'use strict';
    let nextButton =
        window.document.querySelector('.img-slider-controls .next');
    let prevButton =
        window.document.querySelector('.img-slider-controls .prev');
    let imgSliderElement = window.document.getElementById('img-slider');
    let imgSlider = new ImageSlider(imgSliderElement, nextButton, prevButton);
}(this));
