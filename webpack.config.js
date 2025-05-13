/**
 * SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */
const CopyWebpackPlugin = require('copy-webpack-plugin');
const webpack = require('webpack');

const base = './nextcloudappstore/core/static/';

module.exports = {
    entry: {
        'app/list': `${base}assets/app/app/views/List.ts`,
        'app/detail': `${base}assets/app/app/views/Detail.ts`,
        'app/register': `${base}assets/app/app/views/Register.ts`,
        'app/upload': `${base}assets/app/app/views/Upload.ts`,
        'app/releases': `${base}assets/app/app/views/Releases.ts`,
        'user/token': `${base}assets/app/user/views/Token.ts`
    },
    output: {
        path: __dirname,
        filename: `${base}public/[name].js`
    },
    resolve: {
        // Add '.ts' and '.tsx' as a resolvable extension.
        extensions: ['.webpack.js', '.web.js', '.ts', '.tsx', '.js']
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: 'ts-loader'
            }
        ]
    },
    plugins: [
        // we dont care about bootstrap, jquery or polyfills, just copy it from
        // node_modules to the vendor directory for each page load to include
        new CopyWebpackPlugin({
            patterns: [
                {
                    from: 'node_modules/bootstrap/dist/fonts',
                    to: `${base}vendor/bootstrap/dist/fonts`
                },
                {
                    from: 'node_modules/bootstrap/dist/css/bootstrap.min.css',
                    to: `${base}vendor/bootstrap/dist/css/bootstrap.min.css`
                },
                {
                    from: 'node_modules/bootstrap.native/dist/bootstrap-native.min.js',
                    to: `${base}vendor/bootstrap.native.min.js`
                },
                {
                    from: 'node_modules/highlight.js/styles/github.css',
                    to: `${base}vendor/github.css`
                },
            ]
        }),
        new webpack.NormalModuleReplacementPlugin(
            /node_modules\/highlight\.js\/lib\/index\.js/,
            '../../../nextcloudappstore/core/static/assets/patches/hl.js'
        )
    ]
};
