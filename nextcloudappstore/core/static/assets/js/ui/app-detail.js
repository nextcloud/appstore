(function (global) {
    'use strict';

    function load_comments(languageCode) {
        fetchRatings(ratingUrl, languageCode, fallbackLang)
            .then((result) => {
                const ratings = result.ratings;
                const ratingLang = result.lang;
                ratingContainer.classList.remove('loading');
                ratingContainer.innerHTML = '';
                if (ratings.length > 0) {
                    ratings.forEach((rating) => {
                        const result = renderRating(ratingTpl, rating, ratingLang);
                        ratingContainer.appendChild(result);
                        commentLangInput.value = ratingLang;
                    });
                } else {
                    const result = renderEmptyRatings(noRatingTpl);
                    ratingContainer.appendChild(result);
                }
            });
    }

    // init image slider
    let imgEls = Array.from(document.querySelectorAll('.img-slider .img'));
    let imgURLs = imgEls.map((img) => img.src);

    if (imgURLs.length > 0) {
        let firstImg = new Image();
        firstImg.addEventListener('load', () => {
            let sliderLogic = new global.SliderLogic(imgURLs, 0);
            new global.ImageSlider(sliderLogic, document.querySelector('.img-slider'));
        });
        firstImg.src = imgURLs[0];
    }

    // language selection for posting
    function load_language(lang) {
        commentInput.readOnly = true;
        fetchRatings(ratingUrl + "?current_user=true&lang=" + lang, lang)
            .then((result) => {
                let value = '';
                let ratings = result.ratings;
                if (ratings.length > 0) {
                    value = ratings[0].comment;
                }
                commentInput.value = value;
                commentInput.readOnly = false;
            }).catch(() => commentInput.readOnly = false);
    }

    languageInput.addEventListener('change', (event) => {
        load_language(event.target.value);
    });

    // create markdown for app description
    fetchDescription(descriptUrl)
        .then((description) => {
            descriptContainer.innerHTML = description;
            descriptContainer.classList.remove('loading')
        });

    commentLangInput.addEventListener('change', (event) => {
        load_comments(event.target.value);
    });

    load_comments(currentLang, true);
}(this));
