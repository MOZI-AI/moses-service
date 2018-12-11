const webpack = require("webpack");
const merge = require("webpack-merge");
const UglifyJSPlugin = require("uglifyjs-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");

const common = require("./webpack.common.js");

module.exports = merge(common, {
  mode: "production",

  plugins: [
    new webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production")
    })
    //   ,
    // new UglifyJSPlugin({
    //   sourceMap: true,
    //   uglifyOptions: {
    //     compress: true,
    //     mangle: true,
    //     warnings: false
    //   }
    // }),
    // new CompressionPlugin({
    //   test: /\.js/,
    //   filename(asset) {
    //     return asset.replace(".gz", "");
    //   }
    // }),
    // new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
  ]
});
