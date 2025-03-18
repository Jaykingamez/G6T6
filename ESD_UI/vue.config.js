module.exports = {
  publicPath: process.env.NODE_ENV === 'production' ? '/singapore-journey-planner/' : '/',
  lintOnSave: false,
  devServer: {
    historyApiFallback: true,
    client: {
      overlay: true
    }
  }
}