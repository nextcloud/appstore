const CopyWebpackPlugin = require('copy-webpack-plugin');

const base = './nextcloudappstore/core/static/';

module.exports = {
    entry: {
        'app/list': `${base}assets/app/app/views/List.ts`,
        'app/detail': `${base}assets/app/app/views/Detail.ts`,
        'app/register': `${base}assets/app/app/views/Register.ts`,
        'app/upload': `${base}assets/app/app/views/Upload.ts`,
        'app/releases': `${base}assets/app/app/views/Releases.ts`,
        'user/token': `${base}assets/app/user/views/Token.ts`,
    },
    output: {
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
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        // we dont care about bootstrap, jquery or polyfills, just copy it from
        // node_modules to the vendor directory for each page load to include
        new CopyWebpackPlugin([
            {from: 'node_modules/bootstrap', to: `${base}vendor/bootstrap/`},
            {from: 'node_modules/jquery', to: `${base}vendor/jquery/`},
            {
                from: 'node_modules/fetch-min/index.js',
                to: `${base}vendor/fetch/index.js`
            },
            {
                from: 'node_modules/highlight.js/styles/github.css',
                to: `${base}vendor/github.css`
            },
        ])
    ]
};
