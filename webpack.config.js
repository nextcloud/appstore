const CopyWebpackPlugin = require('copy-webpack-plugin');

const base = './nextcloudappstore/core/static/';

module.exports = {
    entry: {
        migrate: `${base}assets/app/app/views/Migrate.ts`,
        'app/list': `${base}assets/app/app/views/List.ts`,
        'app/releases': `${base}assets/app/app/views/Releases.ts`,
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
                enforce: 'pre',
                loader: 'tslint-loader',
                options: {
                    configFile: './tslint.json',
                    failOnHint: true,
                }
            },
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
            {from: 'node_modules/bootstrap', to: base + 'vendor/bootstrap/'},
            {from: 'node_modules/jquery', to: base + 'vendor/jquery/'},
            {from: 'node_modules/whatwg-fetch', to: base + 'vendor/fetch/'},
        ])
    ]
};
