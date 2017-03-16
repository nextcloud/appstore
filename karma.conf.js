module.exports = function (config) {
    config.set({
        basePath: 'nextcloudappstore/core/static/assets/js/',
        frameworks: ['jasmine'],
        files: [
            'app/**/*.js',
            'test/**/*Spec.js',
        ],
        exclude: [],
        preprocessors: {},
        reporters: ['progress'],
        port: 9876,
        colors: true,
        logLevel: config.LOG_INFO,
        autoWatch: true,
        browsers: ['Firefox'],
        singleRun: false,
        concurrency: Infinity
    })
};
