'use strict';

const path = require('path');
const glob = require('glob');
const webpack = require('webpack');

const BabiliPlugin = require("babili-webpack-plugin");
const ExtractTextPlugin = require('extract-text-webpack-plugin');

// Modules
// var autoprefixer = require('autoprefixer');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');

/**
 * Env
 * Get npm lifecycle event to identify the environment
 */
var ENV = process.env.npm_lifecycle_event;
var isProd = (ENV === 'build' || ENV === 'watch');

module.exports = function makeWebpackConfig () {
    /**
     * Config
     * Reference: http://webpack.github.io/docs/configuration.html
     * This is the object where all configuration gets set
     */
    var config = {};

    config.context = __dirname,

    /**
     * Entry
     * Reference: http://webpack.github.io/docs/configuration.html#entry
     * Should be an empty object if it's generating a test build
     * Karma will set this when it's a test build
     */

    config.entry = {
        app: [
            'babel-polyfill',
            './src/app.js',
        ],
    };

    /**
     * Output
     * Reference: http://webpack.github.io/docs/configuration.html#output
     * Should be an empty object if it's generating a test build
     * Karma will handle setting it up for you when it's a test build
     */
    config.output = {
        // Absolute output directory
        path: path.join(__dirname, 'media', 'dist'),

        // Output path from the view of the page
        // Uses webpack-dev-server in development
        // publicPath: isProd ? '/' : 'http://localhost:8080/',
        publicPath: '/',

        // Filename for entry points
        // Only adds hash in build mode
        filename: '[name].min.js',
        // filename: isProd ? '[name].[hash].js' : '[name].bundle.js',

        // Filename for non-entry points
        // Only adds hash in build mode
        chunkFilename: '[name].min.js'
        // chunkFilename: isProd ? '[name].[hash].js' : '[name].bundle.js'
    };

    /**
     * Devtool
     * Reference: http://webpack.github.io/docs/configuration.html#devtool
     * Type of sourcemap to use per build type
     */
    if (isProd) {
        config.devtool = undefined;
        // config.devtool = 'source-map';
    } else {
        config.devtool = 'eval-source-map';
    }

    /**
     * Loaders
     * Reference: http://webpack.github.io/docs/configuration.html#module-loaders
     * List: http://webpack.github.io/docs/list-of-loaders.html
     * This handles most of the magic responsible for converting modules
     */

    // Initialize module
    config.module = {
        rules: [{
            // JS LOADER
            // Reference: https://github.com/babel/babel-loader
            // Transpile .js files using babel-loader
            // Compiles ES6 and ES7 into ES5 code
            test: /\.js$/,
            exclude: [
                path.join(__dirname, 'node_modules'),
            ],
            use: [{
                loader: 'babel-loader',
                options: {
                    cacheDirectory: true,
                    presets: [["env", {
                        modules: false,
                    }]],
                    // presets: [["es2015", { modules: false }]],
                    plugins: [
                    //  'transform-object-assign',
                    //  'transform-es2015-block-scoping',
                        'angularjs-annotate',
                    ],
                }
            }]
        }, {
            // CSS and SCSS LOADER
            test: /\.s?css$/,
            loader: ExtractTextPlugin.extract({
                fallback: "style-loader",
                use: [
                    {
                        loader: 'css-loader', options: {
                            sourceMap: true,
                            minimize: true,
                        },
                    },
                    {
                        loader: 'postcss-loader', options: {
                            sourceMap: true,
                            plugins: () =>[
                                require('autoprefixer')({
                                    grid: false,
                                    browsers: ['last 2 version'],
                                })
                            ],
                        },
                    },
                    {
                        loader: 'sass-loader', options: {
                            sourceMap: true,
                            includePaths: [
                                path.join(__dirname, 'src'),
                                path.join(__dirname, 'node_modules'),
                            ],
                        },
                    },
                ],
            })
        }, {
            // ASSET LOADER
            // Reference: https://github.com/webpack/file-loader
            // Copy png, jpg, jpeg, gif, svg, woff, woff2, ttf, eot files to output
            // Rename the file using the asset hash
            // Pass along the updated reference to your code
            // You can add here any file extension you want to get copied to your output
            test: /\.(png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$/,
            loader: 'file-loader?name=assets/[name].[ext]?[sha1:hash:hex]&publicPath=/media/dist/'
        }, {
            // HTML LOADER
            // Reference: https://github.com/webpack/raw-loader
            // Allow loading html through js
            test: /\.html$/,
            use: [{
                loader: 'html-loader',
                options: {
                    minimize: true,
                    removeComments: true,
                    collapseWhitespace: true,
                },
            }]
        }]
    };

    /**
     * Plugins
     * Reference: http://webpack.github.io/docs/configuration.html#plugins
     * List: http://webpack.github.io/docs/list-of-plugins.html
     */
    config.plugins = [];

    // Reference: https://github.com/ampedandwired/html-webpack-plugin
    // Render index.html
    config.plugins.push(
        new HtmlWebpackPlugin({
            template: './src/index.html',
            inject: 'body'
        }),

        // Reference: https://github.com/webpack/extract-text-webpack-plugin
        // Extract css files
        // Disabled when in test mode or not in build mode
        // new ExtractTextPlugin('[name].[hash].css', {disable: !isProd})
        new ExtractTextPlugin('[name].min.css')
    )

    // Add build specific plugins
    if (isProd) {
        config.plugins.push(
            // Reference: https://github.com/webpack-contrib/babili-webpack-plugin
            new BabiliPlugin(),
            
            // Reference: http://webpack.github.io/docs/list-of-plugins.html#noerrorsplugin
            // Only emit files when there are no errors
            new webpack.NoEmitOnErrorsPlugin(),
            
            // Copy assets from the public folder
            // Reference: https://github.com/kevlened/copy-webpack-plugin
            new CopyWebpackPlugin([], {
              copyUnmodified: false,
            })
        )
    }

    config.plugins.push(
        new webpack.DefinePlugin({
            'DEBUG': !(ENV === 'build'),
            'BUILD': JSON.stringify(require(path.join(__dirname, 'package.json')).version),
            // Sync the breakpoints with your css files!
            'BREAKPOINTS': JSON.stringify({
                xl: "1200px",
                lg: "992px",
                md: "768px",
                sm: "576px",
                xs: "0",
            }),
        })
    )

    /**
     * Dev server configuration
     * Reference: http://webpack.github.io/docs/configuration.html#devserver
     * Reference: http://webpack.github.io/docs/webpack-dev-server.html
     */
    config.devServer = {
        host: '0.0.0.0',
        stats: 'minimal',
        quiet: true,
        contentBase: path.join(__dirname, 'src'),
    };

    return config;
}();
