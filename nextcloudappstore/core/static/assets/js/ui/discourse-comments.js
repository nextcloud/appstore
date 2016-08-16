window.DiscourseEmbed = {
    discourseUrl: 'https://help.nextcloud.com/'
};

(function() {
    let discourseUrl = document.getElementById('discourse-link').href;
    DiscourseEmbed.topicId = discourseUrl.split('/').pop();
})();
