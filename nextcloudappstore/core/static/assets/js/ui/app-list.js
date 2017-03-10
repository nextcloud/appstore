(function (global) {
    'use strict';

    const id = global.id;

    // reload page if featured checkbox is checked
    const form = id('filter-form');
    Array.from(form.querySelectorAll('.auto-submit'))
        .forEach((input) => {
            input.addEventListener('change', () => form.submit());
        });

}(this));
