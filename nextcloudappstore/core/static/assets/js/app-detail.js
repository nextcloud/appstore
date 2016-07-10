(function (global) {
    'use strict';

    class ImageSlider {

        constructor(element, controlsElement) {
            this.element = element;
            this.strip =
                new ImageStrip(this.element.querySelector('.img-strip'));
            let imgCount = this.strip.images.length;
            this.controls = new SliderControls(controlsElement, this, imgCount);
            this.curSlide = 0;
            this.setSlide(this.curSlide);
        }

        setSlide(slide) {
            let imgSpacing = 4;
            let borders = 2;
            let imgWidth = this.element.offsetWidth + imgSpacing - borders;
            let curHeight = this.strip.images[slide].element.offsetHeight;
            this.element.style.height = curHeight + 'px';
            this.strip.setPosX(imgWidth * slide);
            this.controls.setActive(slide);
            this.curSlide = slide;
        }

        increment(steps) {
            let imgCount = this.strip.images.length;
            let next = this.curSlide + steps;
            next = ((next % imgCount) + imgCount) % imgCount; // because a simple % does it wrong
            this.setSlide(next);
        }
    }


    class SliderControls {

        constructor(element, slider, imgCount) {
            this.element = element;
            this.nextBtn = this.element.querySelector('.next');
            this.prevBtn = this.element.querySelector('.prev');
            this.nav = new SliderNav(this.element.querySelector('.slider-nav'),
                    slider, imgCount);

            this.nextBtn.addEventListener('click', function () {
                slider.increment(1);
            });
            this.prevBtn.addEventListener('click', function () {
                slider.increment(-1);
            });
        }

        setActive(index) {
            this.nav.setActive(index);
        }
    }

    class SliderNav {

        constructor(element, slider, imgCount) {
            this.element = element;
            this.slider = slider;
            this.imgCount = imgCount;
            this.btns = this.generateButtons();
        }

        generateButtons() {
            let btns = []
            for (let i = 0; i < this.imgCount; i++) {
                let btn = document.createElement('a');
                let slider = this.slider;
                btn.addEventListener('click', function() {
                    slider.setSlide(i);
                });
                this.element.appendChild(btn);
                btns.push(btn);
            }
            return btns;
        }

        setActive(index) {
            this.btns.forEach(function(btn) {
                btn.style.opacity = '';
            });
            this.btns[index].style.opacity = 1;
        }
    }


    class ImageStrip {

        constructor(element) {
            this.element = element;
            this.images = this.findImages();
        }

        findImages(element) {
            let imgElements = Array.from(this.element.querySelectorAll('.img'));
            return imgElements.map(function (img) {
                return new Image(img);
            });
        }

        setPosX(posX) {
            this.element.style.right = posX + 'px';
        }
    }


    class Image {

        constructor(element) {
            this.element = element;
        }
    }


    let document = global.document;
    let hljs = global.hljs;
    let md = global.markdownit({
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(lang, str).value;
                } catch (__) {}
            }

            return ''; // use external default escaping
        }
    });

    let imgSliderElement = document.getElementById('img-slider');
    let sliderControlsElement = document.querySelector('.img-slider-controls');
    let imgSlider = new ImageSlider(imgSliderElement, sliderControlsElement);

    // create markdown for app description
    let appDescriptionUrl = document.querySelector('meta[name="nextcloudappstore-app-detail-url"]');
    let descriptionTarget = document.querySelector('.app-description');
    fetch(appDescriptionUrl.content).then((response) => {
        return response.text()
    }).then((description) => {
        descriptionTarget.classList.remove('loading');
        descriptionTarget.innerHTML = md.render(description);
    });
}(this));
