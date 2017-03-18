const CopyWebpackPlugin = require('copy-webpack-plugin');

const base = './nextcloudappstore/core/static/';

module.exports = {
    entry: {
        list: `${base}assets/app/app/views/List.ts`,
        detail: `${base}assets/app/app/views/Detail.ts`,
    },
    output: {
        filename: `${base}public/[name].js`
    },
    resolve: {
        // Add '.ts' and '.tsx' as a resolvable extension.
        extensions: ['.webpack.js', '.web.js', '.ts', '.tsx', '.js']
    },
    module: {
        loaders: [
            {test: /\.tsx?$/, loader: 'ts-loader'}
        ]
    },
    plugins: [
        // we dont care about bootstrap, jquery or polyfills, just copy it from
        // node_modules to the vendor directory for each page load to include
        new CopyWebpackPlugin([
            {from: 'node_modules/bootstrap', to: base + 'vendor/bootstrap/'},
            {from: 'node_modules/jquery', to: base + 'vendor/jquery/'},
            {from: 'node_modules/whatwg-fetch', to: base + 'vendor/fetch/'},
        ])
    ]
};
