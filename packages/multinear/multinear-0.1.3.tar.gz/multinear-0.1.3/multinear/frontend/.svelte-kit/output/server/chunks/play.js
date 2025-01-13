import { Z as spread_props, _ as slot, $ as sanitize_props } from "./index.js";
import { I as Icon } from "./Icon.js";
function Play($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "polygon",
      { "points": "6 3 20 12 6 21 6 3" }
    ]
  ];
  Icon($$payload, spread_props([
    { name: "play" },
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
export {
  Play as P
};
