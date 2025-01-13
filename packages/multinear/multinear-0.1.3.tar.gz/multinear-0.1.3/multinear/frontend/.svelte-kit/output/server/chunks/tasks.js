import { a3 as fallback, a0 as ensure_array_like, W as escape_html, Y as bind_props, R as pop, P as push, T as attr } from "./index.js";
import "./index3.js";
import { L as Label } from "./TimeAgo.js";
import { B as Button } from "./projects.js";
function StatusFilter($$payload, $$props) {
  push();
  let availableStatuses;
  let statusFilter = fallback($$props["statusFilter"], "");
  let statusCounts = fallback($$props["statusCounts"], () => ({}), true);
  let totalCount = $$props["totalCount"];
  let selectedFilter = fallback($$props["selectedFilter"], false);
  let selectedCount = fallback($$props["selectedCount"], null);
  availableStatuses = Object.entries(statusCounts).filter(([_, count]) => count > 0).map(([status]) => status);
  const each_array = ensure_array_like(availableStatuses);
  $$payload.out += `<div class="flex flex-col space-y-1.5">`;
  Label($$payload, {
    children: ($$payload2) => {
      $$payload2.out += `<!---->Filter`;
    },
    $$slots: { default: true }
  });
  $$payload.out += `<!----> <div class="flex gap-2">`;
  Button($$payload, {
    variant: "outline",
    size: "sm",
    class: statusFilter === "" && !selectedFilter ? "bg-gray-100 border-gray-200" : "",
    children: ($$payload2) => {
      $$payload2.out += `<!---->All tasks (${escape_html(totalCount)})`;
    },
    $$slots: { default: true }
  });
  $$payload.out += `<!----> `;
  if (selectedCount !== null && selectedCount > 0) {
    $$payload.out += "<!--[-->";
    Button($$payload, {
      variant: "outline",
      size: "sm",
      class: selectedFilter ? "bg-blue-50 border-blue-200 text-blue-700" : "",
      children: ($$payload2) => {
        $$payload2.out += `<!---->Selected (${escape_html(selectedCount)})`;
      },
      $$slots: { default: true }
    });
  } else {
    $$payload.out += "<!--[!-->";
  }
  $$payload.out += `<!--]--> <!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let status = each_array[$$index];
    Button($$payload, {
      variant: "outline",
      size: "sm",
      class: `
                    ${status === "completed" ? "text-green-700" : status === "failed" ? "text-red-700" : "text-gray-700"}
                    ${statusFilter === status && !selectedFilter ? status === "completed" ? "bg-green-50 border-green-200" : status === "failed" ? "bg-red-50 border-red-200" : "bg-gray-50 border-gray-200" : ""}
                `,
      children: ($$payload2) => {
        $$payload2.out += `<!---->${escape_html(status)} (${escape_html(statusCounts[status])})`;
      },
      $$slots: { default: true }
    });
  }
  $$payload.out += `<!--]--></div></div>`;
  bind_props($$props, {
    statusFilter,
    statusCounts,
    totalCount,
    selectedFilter,
    selectedCount
  });
  pop();
}
function StatusBadge($$payload, $$props) {
  let status = $$props["status"];
  let className = fallback($$props["className"], "");
  $$payload.out += `<span${attr("class", `inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium border
    ${status === "completed" ? "status-completed status-completed-border" : status === "failed" ? "status-failed status-failed-border" : "status-default status-default-border"} ${className}`)}>${escape_html(status)}</span>`;
  bind_props($$props, { status, className });
}
function getTaskStatus(task) {
  return {
    isPassed: task.eval_passed,
    statusClass: task.eval_passed ? "bg-green-50 hover:bg-green-100" : "bg-red-100 hover:bg-red-200"
  };
}
function truncateInput(input, maxLength = 50) {
  if (!input) return "-";
  const text = typeof input === "object" && "str" in input ? input.str : JSON.stringify(input);
  return text.length > maxLength ? text.slice(0, maxLength) + "..." : text;
}
function filterTasks(tasks, statusFilter, searchTerm, selectedIds = null) {
  return tasks?.filter((task) => {
    if (selectedIds !== null && !selectedIds.includes(task.id)) return false;
    if (statusFilter && task.status !== statusFilter) return false;
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return searchInObject(search, task);
    }
    return true;
  });
}
function getStatusCounts(tasks) {
  return tasks?.reduce((acc, task) => {
    acc[task.status] = (acc[task.status] || 0) + 1;
    return acc;
  }, {}) || {};
}
function searchInObject(searchTerm, obj) {
  if (!obj) return false;
  const search = searchTerm.toLowerCase();
  if (typeof obj === "string") return obj.toLowerCase().includes(search);
  if (typeof obj === "number") return obj.toString().toLowerCase().includes(search);
  if (Array.isArray(obj)) return obj.some((item) => searchInObject(search, item));
  if (typeof obj === "object") {
    return Object.values(obj).some((value) => searchInObject(search, value));
  }
  return false;
}
export {
  StatusFilter as S,
  getTaskStatus as a,
  StatusBadge as b,
  filterTasks as f,
  getStatusCounts as g,
  truncateInput as t
};
