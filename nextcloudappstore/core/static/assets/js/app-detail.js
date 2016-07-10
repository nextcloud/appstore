(function (global) {
    'use strict';

    class ImageSlider {

        constructor(element) {
            this.element = element;
            this.parent = element.parentNode;
            this.view = element.querySelector('.img-slider-view');
            this.strip = new ImageStrip(element.querySelector('.img-strip'));
            let imgCount = this.strip.images.length;
            this.controls = new SliderControls(
                    element.querySelector('.img-slider-controls'),
                    this, imgCount);
            this.curSlide = 0;
            this.setSlide(this.curSlide);

            element.querySelector('.fullscreen-btn').addEventListener('click', () => {
                this.openFullscreen();
            });
            element.querySelector('.close-fullscreen-btn').addEventListener('click', () => {
                this.closeFullscreen();
            });
        }

        setSlide(slide) {
            let imgSpacing = 4;
            let imgWidth = this.view.offsetWidth + imgSpacing;
            let curHeight = this.strip.images[slide].offsetHeight;
            this.view.style.height = curHeight + 'px';
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

        openFullscreen() {
            let fullscreen = document.createElement('div');
            fullscreen.className = 'fullscreen';
            fullscreen.appendChild(this.element);
            document.querySelector('body').appendChild(fullscreen);
            this.setSlide(this.curSlide);
        }

        closeFullscreen() {
            this.parent.appendChild(this.element);
            let fullscreen = document.querySelector('.fullscreen');
            if (fullscreen) fullscreen.remove();
            this.setSlide(this.curSlide);
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
            let btns = [];
            for (let i = 0; i < this.imgCount; i++) {
                let btn = document.createElement('a');
                btn.addEventListener('click', () => {
                    this.slider.setSlide(i);
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
            this.images = Array.from(this.element.querySelectorAll('.img'));
        }

        setPosX(posX) {
            this.element.style.right = posX + 'px';
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

    let imgSliderElement = document.querySelector('.img-slider');
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
