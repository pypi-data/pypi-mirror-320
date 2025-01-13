import { S as store_get, X as unsubscribe_stores, R as pop, P as push } from "../../../chunks/index.js";
import "../../../chunks/client.js";
import { l as getRecentRuns } from "../../../chunks/TimeAgo.js";
import { s as selectedProjectId, e as searchTerm } from "../../../chunks/projects.js";
import { R as RunsWithFilters } from "../../../chunks/RunsWithFilters.js";
function _page($$payload, $$props) {
  push();
  var $$store_subs;
  let runs = [];
  let loading = true;
  let error = null;
  let localSearchTerm = "";
  async function loadData() {
    loading = true;
    error = null;
    try {
      const response = await getRecentRuns(store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId), 100, 0);
      runs = response.runs;
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load runs";
      console.error(e);
    } finally {
      loading = false;
    }
  }
  {
    if (store_get($$store_subs ??= {}, "$searchTerm", searchTerm)) {
      localSearchTerm = store_get($$store_subs ??= {}, "$searchTerm", searchTerm);
    }
  }
  if (store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId)) {
    loadData();
  }
  $$payload.out += `<div class="container mx-auto p-4 space-y-6"><h1 class="text-3xl font-bold">Experiments</h1> `;
  RunsWithFilters($$payload, {
    runsList: runs,
    isLoading: loading,
    loadingError: error,
    showViewAll: false,
    showFilters: true,
    initialSearchTerm: localSearchTerm
  });
  $$payload.out += `<!----></div>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
export {
  _page as default
};
