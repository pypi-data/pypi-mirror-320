import { Z as spread_props, _ as slot, $ as sanitize_props, a3 as fallback, W as escape_html, Y as bind_props } from "./index.js";
import { I as Icon } from "./Icon.js";
function Loader_circle($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      { "d": "M21 12a9 9 0 1 1-6.219-8.56" }
    ]
  ];
  Icon($$payload, spread_props([
    { name: "loader-circle" },
    $$sanitized_props,
    {
      iconNode,
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {}, null);
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
}
function Loading($$payload, $$props) {
  let message = fallback($$props["message"], "Loading...");
  $$payload.out += `<div class="flex items-center justify-center py-8 text-gray-500"><div class="flex items-center gap-2">`;
  Loader_circle($$payload, { class: "h-6 w-6 animate-spin" });
  $$payload.out += `<!----> <span>${escape_html(message)}</span></div></div>`;
  bind_props($$props, { message });
}
export {
  Loader_circle as L,
  Loading as a
};
