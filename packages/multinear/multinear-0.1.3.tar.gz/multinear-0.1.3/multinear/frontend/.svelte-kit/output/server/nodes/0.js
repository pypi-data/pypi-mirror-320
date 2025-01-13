import * as universal from '../entries/pages/_layout.ts.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.ts";
export const imports = ["_app/immutable/nodes/0.Dcp6fqjA.js","_app/immutable/chunks/disclose-version.BjBLbfIf.js","_app/immutable/chunks/index-client.BoCi2Vgn.js","_app/immutable/chunks/index.DxvZjEHL.js","_app/immutable/chunks/legacy.b-VaXUeO.js","_app/immutable/chunks/props.Cy3ILhV4.js","_app/immutable/chunks/index.CZPF9jM2.js","_app/immutable/chunks/stores.BfidqmOg.js","_app/immutable/chunks/entry.C16cB7Ci.js","_app/immutable/chunks/index.Dvh8W8ZQ.js","_app/immutable/chunks/projects.C_-bKb6m.js"];
export const stylesheets = ["_app/immutable/assets/0.DbnLbwCF.css"];
export const fonts = [];
