window.DiscourseEmbed = {
    discourseUrl: 'https://help.nextcloud.com/'
};

(function() {
    'use strict';
    let discourseUrl = document.getElementById('discourse-link').href;
    DiscourseEmbed.topicId = discourseUrl.split('/').pop();
})();
