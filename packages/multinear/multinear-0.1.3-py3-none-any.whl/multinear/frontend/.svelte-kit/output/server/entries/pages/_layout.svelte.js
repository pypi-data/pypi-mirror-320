import { S as store_get, T as attr, V as stringify, W as escape_html, X as unsubscribe_stores, Y as bind_props, R as pop, P as push, Z as spread_props, _ as slot, $ as sanitize_props, a0 as ensure_array_like } from "../../chunks/index.js";
import "../../chunks/index3.js";
import { p as page } from "../../chunks/stores.js";
import { B as Button, s as selectedProjectId, a as selectedChallengeId } from "../../chunks/projects.js";
import "../../chunks/client.js";
import { I as Icon } from "../../chunks/Icon.js";
const logo = "/_app/immutable/assets/logo.o9F5wtRW.png";
function NavLink($$payload, $$props) {
  push();
  var $$store_subs;
  let isActive;
  let href = $$props["href"];
  let label = $$props["label"];
  function checkIsActive(href2, pathname) {
    return href2 === pathname || href2.split("#")[0].startsWith(`${pathname}`) || `${href2.split("#")[0]}/`.startsWith(`${pathname}`) || href2 === "/" && pathname.startsWith("/dashboard");
  }
  isActive = checkIsActive(href, store_get($$store_subs ??= {}, "$page", page).url.pathname);
  $$payload.out += `<a${attr("href", href)} class="block">`;
  Button($$payload, {
    variant: "ghost",
    class: `hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full ${stringify(isActive ? "active-nav" : "")}`,
    children: ($$payload2) => {
      $$payload2.out += `<!---->${escape_html(label)}`;
    },
    $$slots: { default: true }
  });
  $$payload.out += `<!----></a>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { href, label });
  pop();
}
function Book($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"
      }
    ]
  ];
  Icon($$payload, spread_props([
    { name: "book" },
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
function _layout($$payload, $$props) {
  push();
  var $$store_subs;
  let { children } = $$props;
  const baseNavLinks = [{ href: "/", label: "Home" }];
  const navLinks = (() => {
    const pathname = store_get($$store_subs ??= {}, "$page", page).url.pathname;
    let links = [...baseNavLinks];
    if (store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId)) {
      links.push({
        href: `/experiments#${store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId)}`,
        label: "Experiments"
      });
    }
    if (pathname.startsWith("/run")) {
      links.push({
        href: pathname + store_get($$store_subs ??= {}, "$page", page).url.hash,
        label: "Run"
      });
    }
    if (pathname.startsWith("/compare") || store_get($$store_subs ??= {}, "$selectedChallengeId", selectedChallengeId)) {
      links.push({
        href: `/compare#${store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId)}/c:${store_get($$store_subs ??= {}, "$selectedChallengeId", selectedChallengeId)}`,
        label: "Compare"
      });
    }
    return links;
  })();
  const each_array = ensure_array_like(navLinks);
  $$payload.out += `<div class="min-h-screen flex flex-col"><nav class="bg-gray-800 p-4"><div class="container mx-auto flex justify-between items-center"><div class="flex items-center"><a href="/" class="flex items-center"><img${attr("src", logo)} alt="Logo" class="h-8 w-10 mr-4"> <div class="text-lg text-white font-bold pr-8">Multinear</div></a> <!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let link = each_array[$$index];
    NavLink($$payload, { href: link.href, label: link.label });
  }
  $$payload.out += `<!--]--></div></div></nav> <main class="flex-1 flex">`;
  children($$payload);
  $$payload.out += `<!----></main> <footer class="bg-gray-800 p-4"><div class="container mx-auto flex justify-between items-center text-gray-300"><div><a href="https://multinear.com" target="_blank" rel="noopener noreferrer">© 2025 Multinear.</a></div> <div class="flex items-center"><a href="https://multinear.com" target="_blank" rel="noopener noreferrer">`;
  Button($$payload, {
    variant: "ghost",
    class: "hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full flex items-center space-x-2",
    children: ($$payload2) => {
      Book($$payload2, { class: "h-6 w-6" });
      $$payload2.out += `<!----> <span>Documentation</span>`;
    },
    $$slots: { default: true }
  });
  $$payload.out += `<!----></a> <a href="https://github.com/multinear" target="_blank" rel="noopener noreferrer">`;
  Button($$payload, {
    variant: "ghost",
    class: "hover:bg-gray-700 text-gray-300 hover:text-gray-300 w-full flex items-center space-x-2",
    children: ($$payload2) => {
      $$payload2.out += `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-6 w-6"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.11.82-.26.82-.577v-2.17c-3.338.726-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.73.083-.73 1.205.084 1.84 1.237 1.84 1.237 1.07 1.835 2.807 1.305 3.492.997.108-.775.42-1.305.763-1.605-2.665-.3-5.467-1.332-5.467-5.93 0-1.31.467-2.38 1.235-3.22-.123-.303-.535-1.523.117-3.176 0 0 1.007-.322 3.3 1.23.957-.266 1.983-.398 3.003-.403 1.02.005 2.046.137 3.003.403 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.807 5.625-5.48 5.92.43.37.823 1.102.823 2.222v3.293c0 .32.22.694.825.576C20.565 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"></path></svg> <span>GitHub</span>`;
    },
    $$slots: { default: true }
  });
  $$payload.out += `<!----></a></div></div></footer></div>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
export {
  _layout as default
};
