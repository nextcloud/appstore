module.exports = function (config) {
    config.set({
        basePath: 'nextcloudappstore/core/static/',
        frameworks: ['jasmine', 'requirejs'],
        files: [
            {pattern: 'public/**/*.js', included: false},
            {pattern: 'assets/test/**/*Spec.js', included: false},
            'assets/test/test-main.js',
        ],
        exclude: [],
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
