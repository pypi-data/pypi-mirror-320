import { Q as setContext, a1 as getContext, a2 as rest_props, P as push, a3 as fallback, S as store_get, _ as slot, a4 as spread_attributes, X as unsubscribe_stores, Y as bind_props, R as pop, $ as sanitize_props, Z as spread_props, a5 as copy_payload, a6 as assign_payload, a7 as invalid_default_snippet, a0 as ensure_array_like, W as escape_html, T as attr, V as stringify } from "../../../chunks/index.js";
import "../../../chunks/client.js";
import { formatDuration, intervalToDuration } from "date-fns";
import { E as ErrorDisplay, C as Card, a as Card_header, b as Card_title, c as Card_description } from "../../../chunks/ErrorDisplay.js";
import { t as toWritableStores, o as overridable, c as createBitAttrs, r as removeUndefined, g as getOptionUpdater, a as getSameTasks, L as Label, I as Input, C as Card_content, T as Table, b as Table_header, d as Table_row, e as Table_head, f as Table_body, h as Table_cell, i as TimeAgo } from "../../../chunks/TimeAgo.js";
import "clsx";
import "dequal";
import { o as omit, m as makeElement, d as disabledAttr, e as executeCallbacks, a as addMeltEventListener, k as kbd, s as styleToString } from "../../../chunks/index3.js";
import { d as derived, w as writable } from "../../../chunks/index2.js";
import { C as Check } from "../../../chunks/check.js";
import { I as Icon } from "../../../chunks/Icon.js";
import { d as cn, s as selectedProjectId, a as selectedChallengeId } from "../../../chunks/projects.js";
import { f as filterTasks, g as getStatusCounts, S as StatusFilter, a as getTaskStatus, b as StatusBadge } from "../../../chunks/tasks.js";
import DiffMatchPatch from "diff-match-patch";
const defaults = {
  disabled: false,
  required: false,
  name: void 0,
  value: "on",
  defaultChecked: false
};
function createCheckbox(props) {
  const withDefaults = { ...defaults, ...props };
  const options = toWritableStores(omit(withDefaults, "checked", "defaultChecked"));
  const { disabled, name, required, value } = options;
  const checkedWritable = withDefaults.checked ?? writable(withDefaults.defaultChecked);
  const checked = overridable(checkedWritable, withDefaults?.onCheckedChange);
  const root = makeElement("checkbox", {
    stores: [checked, disabled, required],
    returned: ([$checked, $disabled, $required]) => {
      return {
        "data-disabled": disabledAttr($disabled),
        disabled: disabledAttr($disabled),
        "data-state": $checked === "indeterminate" ? "indeterminate" : $checked ? "checked" : "unchecked",
        type: "button",
        role: "checkbox",
        "aria-checked": $checked === "indeterminate" ? "mixed" : $checked,
        "aria-required": $required
      };
    },
    action: (node) => {
      const unsub = executeCallbacks(addMeltEventListener(node, "keydown", (e) => {
        if (e.key === kbd.ENTER)
          e.preventDefault();
      }), addMeltEventListener(node, "click", () => {
        if (disabled.get())
          return;
        checked.update((value2) => {
          if (value2 === "indeterminate")
            return true;
          return !value2;
        });
      }));
      return {
        destroy: unsub
      };
    }
  });
  const input = makeElement("checkbox-input", {
    stores: [checked, name, value, required, disabled],
    returned: ([$checked, $name, $value, $required, $disabled]) => {
      return {
        type: "checkbox",
        "aria-hidden": true,
        hidden: true,
        tabindex: -1,
        name: $name,
        value: $value,
        checked: $checked === "indeterminate" ? false : $checked,
        required: $required,
        disabled: disabledAttr($disabled),
        style: styleToString({
          position: "absolute",
          opacity: 0,
          "pointer-events": "none",
          margin: 0,
          transform: "translateX(-100%)"
        })
      };
    }
  });
  const isIndeterminate = derived(checked, ($checked) => $checked === "indeterminate");
  const isChecked = derived(checked, ($checked) => $checked === true);
  return {
    elements: {
      root,
      input
    },
    states: {
      checked
    },
    helpers: {
      isIndeterminate,
      isChecked
    },
    options
  };
}
function getCheckboxData() {
  const NAME = "checkbox";
  const PARTS = ["root", "input", "indicator"];
  return {
    NAME,
    PARTS
  };
}
function setCtx(props) {
  const { NAME, PARTS } = getCheckboxData();
  const getAttrs = createBitAttrs(NAME, PARTS);
  const checkbox = { ...createCheckbox(removeUndefined(props)), getAttrs };
  setContext(NAME, checkbox);
  return {
    ...checkbox,
    updateOption: getOptionUpdater(checkbox.options)
  };
}
function getCtx() {
  const { NAME } = getCheckboxData();
  return getContext(NAME);
}
function Checkbox$1($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "checked",
    "disabled",
    "name",
    "required",
    "value",
    "onCheckedChange",
    "asChild",
    "el"
  ]);
  push();
  var $$store_subs;
  let attrs, builder;
  let checked = fallback($$props["checked"], false);
  let disabled = fallback($$props["disabled"], () => void 0, true);
  let name = fallback($$props["name"], () => void 0, true);
  let required = fallback($$props["required"], () => void 0, true);
  let value = fallback($$props["value"], () => void 0, true);
  let onCheckedChange = fallback($$props["onCheckedChange"], () => void 0, true);
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const {
    elements: { root },
    states: { checked: localChecked },
    updateOption,
    getAttrs
  } = setCtx({
    defaultChecked: checked,
    disabled,
    name,
    required,
    value,
    onCheckedChange: ({ next }) => {
      if (checked !== next) {
        onCheckedChange?.(next);
        checked = next;
      }
      return next;
    }
  });
  attrs = {
    ...getAttrs("root"),
    disabled: disabled ? true : void 0
  };
  checked !== void 0 && localChecked.set(checked);
  updateOption("disabled", disabled);
  updateOption("name", name);
  updateOption("required", required);
  updateOption("value", value);
  builder = store_get($$store_subs ??= {}, "$root", root);
  Object.assign(builder, attrs);
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<button${spread_attributes({ ...builder, type: "button", ...$$restProps })}><!---->`;
    slot($$payload, $$props, "default", { builder }, null);
    $$payload.out += `<!----></button>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, {
    checked,
    disabled,
    name,
    required,
    value,
    onCheckedChange,
    asChild,
    el
  });
  pop();
}
function Checkbox_indicator($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["asChild", "el"]);
  push();
  var $$store_subs;
  let attrs;
  let asChild = fallback($$props["asChild"], false);
  let el = fallback($$props["el"], () => void 0, true);
  const {
    helpers: { isChecked, isIndeterminate },
    states: { checked },
    getAttrs
  } = getCtx();
  function getStateAttr(state) {
    if (state === "indeterminate") return "indeterminate";
    if (state) return "checked";
    return "unchecked";
  }
  attrs = {
    ...getAttrs("indicator"),
    "data-state": getStateAttr(store_get($$store_subs ??= {}, "$checked", checked))
  };
  if (asChild) {
    $$payload.out += "<!--[-->";
    $$payload.out += `<!---->`;
    slot(
      $$payload,
      $$props,
      "default",
      {
        attrs,
        isChecked: store_get($$store_subs ??= {}, "$isChecked", isChecked),
        isIndeterminate: store_get($$store_subs ??= {}, "$isIndeterminate", isIndeterminate)
      },
      null
    );
    $$payload.out += `<!---->`;
  } else {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<div${spread_attributes({ ...$$restProps, ...attrs })}><!---->`;
    slot(
      $$payload,
      $$props,
      "default",
      {
        attrs,
        isChecked: store_get($$store_subs ??= {}, "$isChecked", isChecked),
        isIndeterminate: store_get($$store_subs ??= {}, "$isIndeterminate", isIndeterminate)
      },
      null
    );
    $$payload.out += `<!----></div>`;
  }
  $$payload.out += `<!--]-->`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  bind_props($$props, { asChild, el });
  pop();
}
function Minus($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [["path", { "d": "M5 12h14" }]];
  Icon($$payload, spread_props([
    { name: "minus" },
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
function Checkbox($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, ["class", "checked"]);
  push();
  let className = fallback($$props["class"], void 0);
  let checked = fallback($$props["checked"], false);
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    Checkbox$1($$payload2, spread_props([
      {
        class: cn("border-primary ring-offset-background focus-visible:ring-ring data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground peer box-content h-4 w-4 shrink-0 rounded-sm border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[disabled=true]:cursor-not-allowed data-[disabled=true]:opacity-50", className),
        get checked() {
          return checked;
        },
        set checked($$value) {
          checked = $$value;
          $$settled = false;
        }
      },
      $$restProps,
      {
        children: ($$payload3) => {
          Checkbox_indicator($$payload3, {
            class: cn("flex h-4 w-4 items-center justify-center text-current"),
            children: invalid_default_snippet,
            $$slots: {
              default: ($$payload4, { isChecked, isIndeterminate }) => {
                if (isChecked) {
                  $$payload4.out += "<!--[-->";
                  Check($$payload4, { class: "h-3.5 w-3.5" });
                } else {
                  $$payload4.out += "<!--[!-->";
                  if (isIndeterminate) {
                    $$payload4.out += "<!--[-->";
                    Minus($$payload4, { class: "h-3.5 w-3.5" });
                  } else {
                    $$payload4.out += "<!--[!-->";
                  }
                  $$payload4.out += `<!--]-->`;
                }
                $$payload4.out += `<!--]-->`;
              }
            }
          });
        },
        $$slots: { default: true }
      }
    ]));
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  bind_props($$props, { class: className, checked });
  pop();
}
function DiffOutput($$payload, $$props) {
  push();
  let diffs;
  let text1 = $$props["text1"];
  let text2 = $$props["text2"];
  const dmp = new DiffMatchPatch();
  diffs = dmp.diff_main(text1, text2);
  {
    dmp.diff_cleanupSemantic(diffs);
  }
  const each_array = ensure_array_like(diffs);
  $$payload.out += `<div class="text-sm bg-white p-2 rounded border overflow-auto"><!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let [type, text] = each_array[$$index];
    if (type === 0) {
      $$payload.out += "<!--[-->";
      $$payload.out += `<span>${escape_html(text)}</span>`;
    } else {
      $$payload.out += "<!--[!-->";
      if (type === 1) {
        $$payload.out += "<!--[-->";
        $$payload.out += `<span class="bg-green-100 text-green-900">${escape_html(text)}</span>`;
      } else {
        $$payload.out += "<!--[!-->";
        $$payload.out += `<span class="bg-red-100 text-red-900">${escape_html(text)}</span>`;
      }
      $$payload.out += `<!--]-->`;
    }
    $$payload.out += `<!--]-->`;
  }
  $$payload.out += `<!--]--></div>`;
  bind_props($$props, { text1, text2 });
  pop();
}
function _page($$payload, $$props) {
  push();
  var $$store_subs;
  let selectedTasksArray, isComparingTwo, comparisonTasks, filteredTasks, statusCounts, commonInput;
  let loading = true;
  let error = null;
  let tasks = [];
  async function loadTasks() {
    if (!store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId) || !store_get($$store_subs ??= {}, "$selectedChallengeId", selectedChallengeId)) return;
    loading = true;
    error = null;
    try {
      tasks = await getSameTasks(store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId), store_get($$store_subs ??= {}, "$selectedChallengeId", selectedChallengeId));
    } catch (e) {
      error = e instanceof Error ? e.message : "Failed to load tasks";
    } finally {
      loading = false;
    }
  }
  let statusFilter = "";
  let searchTerm = "";
  let selectedTasks = /* @__PURE__ */ new Set();
  let selectedFilter = false;
  function getTaskOutput(task) {
    return typeof task.task_output === "object" && "str" in task.task_output ? task.task_output.str : JSON.stringify(task.task_output, null, 2);
  }
  {
    if (store_get($$store_subs ??= {}, "$selectedProjectId", selectedProjectId) && store_get($$store_subs ??= {}, "$selectedChallengeId", selectedChallengeId)) {
      loadTasks();
    }
  }
  {
    if (selectedTasks.size === 2) {
      selectedFilter = true;
      statusFilter = "";
    }
  }
  selectedTasksArray = Array.from(selectedTasks);
  isComparingTwo = selectedTasksArray.length === 2;
  comparisonTasks = isComparingTwo ? tasks.filter((t) => selectedTasks.has(t.id)) : [];
  filteredTasks = filterTasks(tasks, statusFilter, searchTerm, selectedFilter ? Array.from(selectedTasks) : null);
  statusCounts = getStatusCounts(tasks);
  commonInput = tasks?.[0]?.task_input;
  let $$settled = true;
  let $$inner_payload;
  function $$render_inner($$payload2) {
    $$payload2.out += `<div class="container mx-auto p-4"><div class="flex justify-between items-center mb-4"><h1 class="text-3xl font-bold">Compare Tasks</h1></div> `;
    if (loading) {
      $$payload2.out += "<!--[-->";
      $$payload2.out += `<div class="text-center text-gray-500">Loading tasks...</div>`;
    } else {
      $$payload2.out += "<!--[!-->";
      if (error) {
        $$payload2.out += "<!--[-->";
        ErrorDisplay($$payload2, { errorMessage: error, onRetry: loadTasks });
      } else {
        $$payload2.out += "<!--[!-->";
        if (tasks.length) {
          $$payload2.out += "<!--[-->";
          $$payload2.out += `<div class="space-y-6">`;
          Card($$payload2, {
            children: ($$payload3) => {
              Card_header($$payload3, {
                children: ($$payload4) => {
                  Card_title($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<!---->Common Input`;
                    },
                    $$slots: { default: true }
                  });
                  $$payload4.out += `<!----> `;
                  Card_description($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<div class="bg-white p-2 rounded border overflow-auto" style="white-space: pre-wrap;">${escape_html(typeof commonInput === "object" && "str" in commonInput ? commonInput.str : JSON.stringify(commonInput, null, 2))}</div>`;
                    },
                    $$slots: { default: true }
                  });
                  $$payload4.out += `<!---->`;
                },
                $$slots: { default: true }
              });
            },
            $$slots: { default: true }
          });
          $$payload2.out += `<!----> `;
          Card($$payload2, {
            children: ($$payload3) => {
              Card_header($$payload3, {
                children: ($$payload4) => {
                  Card_description($$payload4, {
                    children: ($$payload5) => {
                      $$payload5.out += `<div class="grid grid-cols-2 gap-4"><div class="space-y-1.5">`;
                      Label($$payload5, {
                        for: "search",
                        children: ($$payload6) => {
                          $$payload6.out += `<!---->Search`;
                        },
                        $$slots: { default: true }
                      });
                      $$payload5.out += `<!----> `;
                      Input($$payload5, {
                        id: "search",
                        placeholder: "Search tasks...",
                        get value() {
                          return searchTerm;
                        },
                        set value($$value) {
                          searchTerm = $$value;
                          $$settled = false;
                        }
                      });
                      $$payload5.out += `<!----></div> `;
                      StatusFilter($$payload5, {
                        get statusFilter() {
                          return statusFilter;
                        },
                        set statusFilter($$value) {
                          statusFilter = $$value;
                          $$settled = false;
                        },
                        get selectedFilter() {
                          return selectedFilter;
                        },
                        set selectedFilter($$value) {
                          selectedFilter = $$value;
                          $$settled = false;
                        },
                        statusCounts,
                        totalCount: tasks.length,
                        selectedCount: selectedTasks.size
                      });
                      $$payload5.out += `<!----></div>`;
                    },
                    $$slots: { default: true }
                  });
                },
                $$slots: { default: true }
              });
            },
            $$slots: { default: true }
          });
          $$payload2.out += `<!----> `;
          Card($$payload2, {
            children: ($$payload3) => {
              Card_content($$payload3, {
                children: ($$payload4) => {
                  Table($$payload4, {
                    children: ($$payload5) => {
                      Table_header($$payload5, {
                        children: ($$payload6) => {
                          Table_row($$payload6, {
                            children: ($$payload7) => {
                              Table_head($$payload7, {
                                class: "w-[50px]",
                                children: ($$payload8) => {
                                  Checkbox($$payload8, {
                                    disabled: true,
                                    checked: selectedTasks.size === filteredTasks.length,
                                    onCheckedChange: (checked) => {
                                      if (checked) {
                                        selectedTasks = new Set(filteredTasks.map((t) => t.id));
                                      } else {
                                        selectedTasks = /* @__PURE__ */ new Set();
                                      }
                                    }
                                  });
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                class: "w-[50%]",
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Output`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!----> `;
                              Table_head($$payload7, {
                                children: ($$payload8) => {
                                  $$payload8.out += `<!---->Details`;
                                },
                                $$slots: { default: true }
                              });
                              $$payload7.out += `<!---->`;
                            },
                            $$slots: { default: true }
                          });
                        },
                        $$slots: { default: true }
                      });
                      $$payload5.out += `<!----> `;
                      Table_body($$payload5, {
                        children: ($$payload6) => {
                          const each_array = ensure_array_like(filteredTasks);
                          $$payload6.out += `<!--[-->`;
                          for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
                            let task = each_array[$$index];
                            const { isPassed, statusClass } = getTaskStatus(task);
                            const isSelected = selectedTasks.has(task.id);
                            Table_row($$payload6, {
                              class: `${statusClass} ${selectedTasks.size === 2 && !isSelected ? "opacity-50" : ""}`,
                              children: ($$payload7) => {
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    Checkbox($$payload8, {
                                      checked: isSelected,
                                      onCheckedChange: (checked) => {
                                        if (checked) {
                                          selectedTasks.add(task.id);
                                        } else {
                                          selectedTasks.delete(task.id);
                                        }
                                        selectedTasks = selectedTasks;
                                      }
                                    });
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    if (isComparingTwo && isSelected) {
                                      $$payload8.out += "<!--[-->";
                                      const otherTask = comparisonTasks.find((t) => t.id !== task.id);
                                      if (otherTask) {
                                        $$payload8.out += "<!--[-->";
                                        DiffOutput($$payload8, {
                                          text1: getTaskOutput(task),
                                          text2: getTaskOutput(otherTask)
                                        });
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]-->`;
                                    } else {
                                      $$payload8.out += "<!--[!-->";
                                      $$payload8.out += `<div class="text-sm bg-white p-2 rounded border overflow-auto">${escape_html(typeof task.task_output === "object" && "str" in task.task_output ? task.task_output.str : JSON.stringify(task.task_output, null, 2))}</div>`;
                                    }
                                    $$payload8.out += `<!--]-->`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!----> `;
                                Table_cell($$payload7, {
                                  children: ($$payload8) => {
                                    $$payload8.out += `<div class="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 items-center"><div class="font-medium text-gray-500 text-sm">ID</div> <div class="font-mono text-sm">${escape_html(task.id.slice(-8))}</div> <div class="font-medium text-gray-500 text-sm">Job</div> <div class="font-mono text-sm"><button class="text-blue-600 hover:underline">${escape_html(task.job_id.slice(-8))}</button></div> <div class="font-medium text-gray-500 text-sm">Model</div> <div class="text-sm">${escape_html(task.task_details.model)}</div> <div class="font-medium text-gray-500 text-sm">Status</div> <div class="flex items-center gap-2">`;
                                    StatusBadge($$payload8, { status: task.status });
                                    $$payload8.out += `<!----> <div class="flex items-center gap-1"><div class="w-16 bg-gray-200 rounded-sm h-2 overflow-hidden flex"><div${attr("class", `h-2 min-w-[3px] ${stringify(isPassed ? "bg-green-600" : "bg-red-600")}`)}${attr("style", `width: ${stringify((task.eval_score * 100).toFixed(0))}%`)}></div></div> <div class="text-xs text-gray-600">${escape_html((task.eval_score * 100).toFixed(0))}%</div></div></div> <div class="font-medium text-gray-500 text-sm">Time</div> <div class="flex items-center gap-3 text-sm text-gray-600">`;
                                    TimeAgo($$payload8, { date: task.created_at });
                                    $$payload8.out += `<!----> `;
                                    if (task.finished_at) {
                                      $$payload8.out += "<!--[-->";
                                      $$payload8.out += `<span class="text-gray-400">·</span> <span>${escape_html(formatDuration(
                                        intervalToDuration({
                                          start: new Date(task.created_at),
                                          end: new Date(task.finished_at)
                                        }),
                                        { format: ["minutes", "seconds"] }
                                      ))}</span>`;
                                    } else {
                                      $$payload8.out += "<!--[!-->";
                                    }
                                    $$payload8.out += `<!--]--></div> `;
                                    if (task.task_details.temperature || task.task_details.max_tokens) {
                                      $$payload8.out += "<!--[-->";
                                      $$payload8.out += `<div class="font-medium text-gray-500 text-sm">Parameters</div> <div class="flex gap-3 text-sm text-gray-600">`;
                                      if (task.task_details.temperature) {
                                        $$payload8.out += "<!--[-->";
                                        $$payload8.out += `<span>temperature: ${escape_html(task.task_details.temperature)}</span>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--> `;
                                      if (task.task_details.max_tokens) {
                                        $$payload8.out += "<!--[-->";
                                        if (task.task_details.temperature) {
                                          $$payload8.out += "<!--[-->";
                                          $$payload8.out += `<span class="text-gray-400">·</span>`;
                                        } else {
                                          $$payload8.out += "<!--[!-->";
                                        }
                                        $$payload8.out += `<!--]--> <span>max tokens: ${escape_html(task.task_details.max_tokens)}</span>`;
                                      } else {
                                        $$payload8.out += "<!--[!-->";
                                      }
                                      $$payload8.out += `<!--]--></div>`;
                                    } else {
                                      $$payload8.out += "<!--[!-->";
                                    }
                                    $$payload8.out += `<!--]--></div>`;
                                  },
                                  $$slots: { default: true }
                                });
                                $$payload7.out += `<!---->`;
                              },
                              $$slots: { default: true }
                            });
                          }
                          $$payload6.out += `<!--]-->`;
                        },
                        $$slots: { default: true }
                      });
                      $$payload5.out += `<!---->`;
                    },
                    $$slots: { default: true }
                  });
                },
                $$slots: { default: true }
              });
            },
            $$slots: { default: true }
          });
          $$payload2.out += `<!----></div>`;
        } else {
          $$payload2.out += "<!--[!-->";
          $$payload2.out += `<div class="text-center text-gray-500">No tasks found</div>`;
        }
        $$payload2.out += `<!--]-->`;
      }
      $$payload2.out += `<!--]-->`;
    }
    $$payload2.out += `<!--]--></div>`;
  }
  do {
    $$settled = true;
    $$inner_payload = copy_payload($$payload);
    $$render_inner($$inner_payload);
  } while (!$$settled);
  assign_payload($$payload, $$inner_payload);
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
export {
  _page as default
};
