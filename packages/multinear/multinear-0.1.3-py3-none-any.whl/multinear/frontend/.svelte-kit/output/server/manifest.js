export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.ico"]),
	mimeTypes: {},
	_: {
		client: {"start":"_app/immutable/entry/start.CT1W8iAT.js","app":"_app/immutable/entry/app.B9xuA_2Z.js","imports":["_app/immutable/entry/start.CT1W8iAT.js","_app/immutable/chunks/entry.C16cB7Ci.js","_app/immutable/chunks/index-client.BoCi2Vgn.js","_app/immutable/chunks/index.CZPF9jM2.js","_app/immutable/entry/app.B9xuA_2Z.js","_app/immutable/chunks/index-client.BoCi2Vgn.js","_app/immutable/chunks/disclose-version.BjBLbfIf.js","_app/immutable/chunks/props.Cy3ILhV4.js"],"stylesheets":[],"fonts":[],"uses_env_dynamic_public":false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js'))
		],
		routes: [
			
		],
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
