const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = (app) => {
	app.use(
		['/v1/currencies', '/v1/rates**'],
		createProxyMiddleware({
			target: process.env.REACT_APP_PROXY_HOST,
			changeOrigin: true,
		}),
	);
};
