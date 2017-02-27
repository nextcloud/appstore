(function (global) {
    'use strict';

    const moment = global.moment;
    const Image = global.Image;
    const hljs = global.hljs;
    const fetch = global.fetch;
    const document = global.document;
    const markdownit = global.markdownit;
    const console = global.console;
    const id = global.id;
    const noReferrerLinks = global.noReferrerLinks;
    const metaVal = global.metaVal;
    const escapeHtml = global.escapeHtml;
    const importNode = document.importNode.bind(document);
    const querySelector = document.querySelector.bind(document);
    const querySelectorAll = document.querySelectorAll.bind(document);

    const ratingUrl = metaVal('nextcloudappstore-app-ratings-url');
    const languageCode = metaVal('language-code');
    const fallbackLang = metaVal('fallback-language-code');
    const ratingTarget = querySelector('.app-rating-list');
    const tmpl = id('app-rating-template').content;
    const tmplNoComments = id('app-rating-template-no-comments').content;

    function createRatingClass(value) {
        // beware: float comparisons
        if (value === 1.0) {
            return 'good';
        } else if (value === 0.0) {
            return 'bad';
        } else {
            return 'ok';
        }
    }

    const md = markdownit({
        highlight: function (str, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(lang, str).value;
                } catch (ex) {
                    console.error(ex);
                }
            }
            return ''; // use external default escaping
        }
    });

    function renderMd(text) {
        return noReferrerLinks(md.render(text));
    }

    function buildUserName(user) {
        let fullName = user.firstName + ' ' + user.lastName;
        if (fullName.trim() === '') {
            fullName = 'Anonymous';
        }
        return escapeHtml(fullName.trim());
    }

    function updateRating(rating, lang) {
        const user = rating.user;
        const fullName = buildUserName(user);
        const comment = rating.translations[lang].comment;
        const escapedComment = renderMd(comment);
        const template = importNode(tmpl, true);
        const className = createRatingClass(rating.rating);
        template.childNodes[1].classList.add(className);
        const relativeDate = moment(rating.ratedAt)
            .locale(lang)
            .fromNow();
        template.querySelector('.date').innerHTML = relativeDate;
        template.querySelector('.author').innerHTML += fullName;
        template.querySelector('.comment').innerHTML = escapedComment;
        ratingTarget.appendChild(template);
    }

    function load_comments(lang, initial = false) {
        fetch(ratingUrl)
            .then((response) => response.json())
            .then((ratings) => {
                ratingTarget.classList.remove('loading');
                ratingTarget.innerHTML = '';
                ratings = ratings
                    .filter(r => r.translations[lang] !== undefined)
                    .filter(r => r.translations[lang].comment !== undefined)
                    .filter(r => r.translations[lang].comment.trim() !== '');
                if (ratings.length > 0) {
                    ratings.forEach((rating) => {
                        updateRating(rating, lang);
                    });
                } else {
                    let langCode = id('comment_display_language_code');
                    let fallback = Array.from(langCode.options)
                        .filter((option) => option.value === fallbackLang);
                    if (initial && fallback.length > 0) {
                        load_comments(fallbackLang);
                        langCode.value = fallbackLang;
                    } else {
                        let noComments = importNode(tmplNoComments, true);
                        ratingTarget.appendChild(noComments);
                    }
                }
            });
    }

    // init image slider
    let imgEls = Array.from(querySelectorAll('.img-slider .img'));
    let imgURLs = imgEls.map((img) => img.src);

    if (imgURLs.length > 0) {
        let firstImg = new Image();
        firstImg.addEventListener('load', () => {
            let sliderLogic = new global.SliderLogic(imgURLs, 0);
            new global.ImageSlider(sliderLogic, querySelector('.img-slider'));
        });
        firstImg.src = imgURLs[0];
    }

    // create markdown for app description
    fetch(metaVal('nextcloudappstore-app-description-url'))
        .then((response) => response.text())
        .then((description) => {
            const target = querySelector('.app-description');
            target.classList.remove('loading');
            target.innerHTML = renderMd(description);
        });

    const langCode = id('comment_display_language_code');
    langCode.addEventListener('change', (event) => {
        load_comments(event.target.value);
    });

    load_comments(languageCode, true);
}(this));
