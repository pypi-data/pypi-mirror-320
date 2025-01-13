import { S as store_get, a0 as ensure_array_like, W as escape_html, X as unsubscribe_stores, R as pop, P as push } from "../../chunks/index.js";
import { E as ErrorDisplay, C as Card, a as Card_header, b as Card_title, c as Card_description } from "../../chunks/ErrorDisplay.js";
import "clsx";
import { g as goto } from "../../chunks/client.js";
import { p as projectsLoading, b as projectsError, c as projects } from "../../chunks/projects.js";
function _page($$payload, $$props) {
  push();
  var $$store_subs;
  function handleProjectSelect(projectId) {
    goto();
  }
  if (!store_get($$store_subs ??= {}, "$projectsLoading", projectsLoading) && !store_get($$store_subs ??= {}, "$projectsError", projectsError) && store_get($$store_subs ??= {}, "$projects", projects).length === 1) {
    handleProjectSelect(store_get($$store_subs ??= {}, "$projects", projects)[0].id);
  }
  $$payload.out += `<div class="container mx-auto flex-1 flex items-center justify-center p-4"><div class="w-96 max-w-2xl space-y-8"><h1 class="text-3xl font-bold text-center mb-8">Projects</h1> `;
  if (store_get($$store_subs ??= {}, "$projectsLoading", projectsLoading)) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<div class="text-center text-gray-500">Loading projects...</div>`;
  } else {
    $$payload.out += "<!--[!-->";
    if (store_get($$store_subs ??= {}, "$projectsError", projectsError)) {
      $$payload.out += "<!--[-->";
      ErrorDisplay($$payload, {
        errorMessage: store_get($$store_subs ??= {}, "$projectsError", projectsError),
        onRetry: () => window.location.reload()
      });
    } else {
      $$payload.out += "<!--[!-->";
      if (store_get($$store_subs ??= {}, "$projects", projects).length === 0) {
        $$payload.out += "<!--[-->";
        $$payload.out += `<div class="text-center text-gray-500">No projects found</div>`;
      } else {
        $$payload.out += "<!--[!-->";
        const each_array = ensure_array_like(store_get($$store_subs ??= {}, "$projects", projects));
        $$payload.out += `<div class="grid gap-4"><!--[-->`;
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let project = each_array[$$index];
          Card($$payload, {
            class: "hover:bg-gray-50 transition-colors",
            children: ($$payload2) => {
              $$payload2.out += `<button class="w-full text-left">`;
              Card_header($$payload2, {
                children: ($$payload3) => {
                  Card_title($$payload3, {
                    children: ($$payload4) => {
                      $$payload4.out += `<!---->${escape_html(project.name)}`;
                    },
                    $$slots: { default: true }
                  });
                  $$payload3.out += `<!----> `;
                  Card_description($$payload3, {
                    class: "pb-4",
                    children: ($$payload4) => {
                      $$payload4.out += `<!---->${escape_html(project.description)}`;
                    },
                    $$slots: { default: true }
                  });
                  $$payload3.out += `<!---->`;
                },
                $$slots: { default: true }
              });
              $$payload2.out += `<!----></button>`;
            },
            $$slots: { default: true }
          });
        }
        $$payload.out += `<!--]--></div>`;
      }
      $$payload.out += `<!--]-->`;
    }
    $$payload.out += `<!--]-->`;
  }
  $$payload.out += `<!--]--></div></div>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
export {
  _page as default
};
