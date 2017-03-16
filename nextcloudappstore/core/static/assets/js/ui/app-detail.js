(function (global) {
    'use strict';
    let document = global.document;
    let ratingUrl = document.querySelector('meta[name="nextcloudappstore-app-ratings-url"]').content;
    let languageCode = document.querySelector('meta[name="language-code"]').content;
    let fallbackLanguageCode = document.querySelector('meta[name="fallback-language-code"]').content;
    let ratingTarget = document.querySelector('.app-rating-list');
    let ratingTemplate = document.getElementById('app-rating-template');
    let ratingTemplateNoComments = document.getElementById('app-rating-template-no-comments');
    let moment = global.moment;
    let hljs = global.hljs;

    let md = global.markdownit({
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(lang, str).value;
                } catch (__) {
                }
            }
            return ''; // use external default escaping
        }
    });

    // create ratings
    let createRatingClass = function (value) {
        // beware: float comparisons
        if (value === 1.0) {
            return 'good';
        } else if (value === 0.0) {
            return 'bad';
        } else {
            return 'ok';
        }
    };

    function load_comments(languageCode, initial=false) {
        fetch(ratingUrl)
            .then((response) => response.json())
            .then((ratings) => {
                ratingTarget.classList.remove('loading');
                ratingTarget.innerHTML = '';
                ratings = ratings
                    .filter(rating => rating.translations[languageCode] !== undefined)
                    .filter(rating => rating.translations[languageCode].comment !== undefined)
                    .filter(rating => rating.translations[languageCode].comment.trim() !== '');
                if( ratings.length > 0) {
                    ratings.forEach((rating) => {
                        let user = rating.user;
                        let fullName = user.firstName + " " + user.lastName;
                        if (fullName.trim() === '') {
                            fullName = 'Anonymous';
                        }
                        let comment = rating.translations[languageCode].comment;
                        let template = document.importNode(ratingTemplate.content, true);
                        template.childNodes[1].classList.add(createRatingClass(rating.rating));
                        let date = moment(rating.ratedAt);
                        template.querySelector('.date').innerHTML = date.locale(languageCode).fromNow();
                        template.querySelector('.author').innerHTML += global.escapeHtml(fullName.trim());
                        template.querySelector('.comment').innerHTML = global.noReferrerLinks(md.render(comment));
                        ratingTarget.appendChild(template);
                    });
                } else {
                    let langCode = global.id('comment_display_language_code');
                    let fallback = Array.from(langCode.options)
                                    .filter( (o) => o.value === fallbackLanguageCode);
                    if(initial && fallback.length > 0) {
                        load_comments(fallbackLanguageCode);
                        langCode.value = fallbackLanguageCode;
                    } else {
                        let templateNoComments = document.importNode(ratingTemplateNoComments.content, true);
                        ratingTarget.appendChild(templateNoComments);
                    }
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

    // create markdown for app description
    let descriptionUrl = document.querySelector('meta[name="nextcloudappstore-app-description-url"]').content;
    let descriptionTarget = document.querySelector('.app-description');
    fetch(descriptionUrl).then((response) => response.text())
        .then((description) => {
            descriptionTarget.classList.remove('loading');
            descriptionTarget.innerHTML = global.noReferrerLinks(md.render(description));
        });

    const langCode = global.id('comment_display_language_code');
    langCode.addEventListener('change', (event) => {
        load_comments(event.target.value);
    });

    load_comments(languageCode, true);
}(this));
